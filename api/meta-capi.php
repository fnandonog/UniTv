<?php
require_once dirname(__DIR__, 2) . '/meta-config.php';

$allowedOrigins = [
    'https://unitvsite.com.br',
    'https://www.unitvsite.com.br',
    'http://localhost:3000',
    'http://127.0.0.1:5500',
    'http://localhost:5500'
];

$requestOrigin = $_SERVER['HTTP_ORIGIN'] ?? '';
$origin = in_array($requestOrigin, $allowedOrigins, true) ? $requestOrigin : 'https://unitvsite.com.br';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: ' . $origin);
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'ok' => false,
        'error' => 'Method not allowed'
    ]);
    exit;
}

function normalize_value($key, $value) {
    $value = trim(mb_strtolower((string)$value));

    if ($key === 'ph') {
        $value = preg_replace('/\D+/', '', $value);
    }

    return $value;
}

function is_sha256($value) {
    return preg_match('/^[a-f0-9]{64}$/i', $value) === 1;
}

function hash_if_needed($value) {
    if (!$value) return null;
    return is_sha256($value) ? strtolower($value) : hash('sha256', $value);
}

try {
    $raw = file_get_contents('php://input');
    $body = json_decode($raw, true);

    if (!is_array($body)) {
        throw new Exception('JSON inválido');
    }

    $eventName = $body['event_name'] ?? null;
    $eventTime = $body['event_time'] ?? time();
    $eventId = $body['event_id'] ?? null;
    $eventSourceUrl = $body['event_source_url'] ?? '';
    $actionSource = $body['action_source'] ?? 'website';
    $customData = $body['custom_data'] ?? [];
    $incomingUserData = $body['user_data'] ?? [];

    if (!$eventName || !$eventId) {
        http_response_code(400);
        echo json_encode([
            'ok' => false,
            'error' => 'event_name e event_id são obrigatórios'
        ]);
        exit;
    }

    $userData = [];
    $fieldsToHash = ['em', 'ph', 'fn', 'ln', 'ct', 'st', 'zp', 'country', 'external_id'];

    foreach ($fieldsToHash as $field) {
        if (!empty($incomingUserData[$field])) {
            $normalized = normalize_value($field, $incomingUserData[$field]);
            if ($normalized) {
                $userData[$field] = hash_if_needed($normalized);
            }
        }
    }

    $userData['client_ip_address'] = $_SERVER['HTTP_CF_CONNECTING_IP']
        ?? $_SERVER['HTTP_X_FORWARDED_FOR']
        ?? $_SERVER['REMOTE_ADDR']
        ?? '';

    $userData['client_user_agent'] = $_SERVER['HTTP_USER_AGENT'] ?? '';

    if (!empty($incomingUserData['fbp'])) {
        $userData['fbp'] = $incomingUserData['fbp'];
    }

    if (!empty($incomingUserData['fbc'])) {
        $userData['fbc'] = $incomingUserData['fbc'];
    }

    $payload = [
        'data' => [
            [
                'event_name' => $eventName,
                'event_time' => $eventTime,
                'event_id' => $eventId,
                'event_source_url' => $eventSourceUrl,
                'action_source' => $actionSource,
                'user_data' => $userData,
                'custom_data' => $customData
            ]
        ]
    ];

    if (defined('META_TEST_EVENT_CODE') && META_TEST_EVENT_CODE) {
        $payload['test_event_code'] = META_TEST_EVENT_CODE;
    }

    $url = 'https://graph.facebook.com/' . META_API_VERSION . '/' . META_PIXEL_ID . '/events?access_token=' . urlencode(META_ACCESS_TOKEN);

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 20
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    curl_close($ch);

    if ($curlError) {
        throw new Exception('Erro cURL: ' . $curlError);
    }

    http_response_code($httpCode >= 200 && $httpCode < 300 ? 200 : 500);

    echo json_encode([
        'ok' => $httpCode >= 200 && $httpCode < 300,
        'meta_status' => $httpCode,
        'meta_response' => json_decode($response, true)
    ]);

} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'ok' => false,
        'error' => $e->getMessage()
    ]);
}
