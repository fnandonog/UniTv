(function () {
  if (window.MetaTracker) return;

  const CONFIG = {
    pixelId: '2204821377087872',
    capiEndpoint: '/api/meta-capi.php',
    capiEnabled: true,
    debug: false
  };

  const STANDARD_EVENTS = new Set([
    'PageView',
    'ViewContent',
    'InitiateCheckout',
    'Contact',
    'Lead',
    'Purchase',
    'CompleteRegistration',
    'Search',
    'AddToCart'
  ]);

  const state = {
    inited: false,
    page: null,
    userData: window.UNITV_META_USER_DATA || {},
    scrollMarks: { 25: false, 50: false, 75: false, 90: false }
  };

  function log(...args) {
    if (CONFIG.debug) console.log('[MetaTracker]', ...args);
  }

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
  }

  function normalizeEmail(value) {
    return (value || '').toString().trim().toLowerCase();
  }

  function normalizePhone(value) {
    return (value || '').toString().replace(/\D+/g, '');
  }

  function normalizeText(value) {
    return (value || '').toString().trim().toLowerCase();
  }

  function mergeUserData(data = {}) {
    const next = { ...state.userData };

    if (data.em) next.em = normalizeEmail(data.em);
    if (data.ph) next.ph = normalizePhone(data.ph);
    if (data.fn) next.fn = normalizeText(data.fn);
    if (data.ln) next.ln = normalizeText(data.ln);

    Object.keys(next).forEach(key => {
      if (!next[key]) delete next[key];
    });

    state.userData = next;
    window.UNITV_META_USER_DATA = next;
  }

  function inferFieldKey(el) {
    const attrs = [
      el.name || '',
      el.id || '',
      el.placeholder || '',
      el.autocomplete || '',
      el.getAttribute('aria-label') || ''
    ].join(' ').toLowerCase();

    if (el.type === 'email' || /e-?mail|mail/.test(attrs)) return 'em';
    if (el.type === 'tel' || /phone|telefone|celular|whatsapp/.test(attrs)) return 'ph';
    if (/first.?name|nome\b/.test(attrs) && !/sobrenome|last/.test(attrs)) return 'fn';
    if (/last.?name|sobrenome/.test(attrs)) return 'ln';

    return null;
  }

  function captureField(el) {
    if (!el || !('value' in el)) return;
    const key = inferFieldKey(el);
    if (!key) return;
    mergeUserData({ [key]: el.value });
  }

  function bindAdvancedMatching() {
    document.querySelectorAll('input, textarea, select').forEach(captureField);
    document.addEventListener('input', e => captureField(e.target), true);
    document.addEventListener('change', e => captureField(e.target), true);
    document.addEventListener('blur', e => captureField(e.target), true);
  }

  function ensurePixel() {
    if (window.fbq) return;

    !(function(f,b,e,v,n,t,s){
      if(f.fbq)return;
      n=f.fbq=function(){n.callMethod ? n.callMethod.apply(n,arguments) : n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;
      n.push=n;
      n.loaded=!0;
      n.version='2.0';
      n.queue=[];
      t=b.createElement(e);
      t.async=!0;
      t.src=v;
      s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s);
    })(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    fbq('init', CONFIG.pixelId);
  }

  function ensureNoscript() {
    if (document.getElementById('meta-pixel-noscript')) return;
    const ns = document.createElement('noscript');
    ns.id = 'meta-pixel-noscript';
    ns.innerHTML = `<img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=${CONFIG.pixelId}&ev=PageView&noscript=1"/>`;
    document.body.prepend(ns);
  }

  function generateEventId(prefix = 'meta') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  }

  function trackBrowser(eventName, params = {}, eventID) {
    ensurePixel();

    if (!window.fbq) return;

    if (STANDARD_EVENTS.has(eventName)) {
      fbq('track', eventName, params, { eventID });
    } else {
      fbq('trackCustom', eventName, params, { eventID });
    }
  }

  function sendToCAPI(payload) {
    if (!CONFIG.capiEnabled || !CONFIG.capiEndpoint) return;

    try {
      const body = JSON.stringify(payload);

      if (navigator.sendBeacon) {
        const blob = new Blob([body], { type: 'application/json' });
        navigator.sendBeacon(CONFIG.capiEndpoint, blob);
      } else {
        fetch(CONFIG.capiEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body,
          keepalive: true
        }).catch(() => {});
      }
    } catch (e) {
      log('Erro CAPI', e);
    }
  }

  function track(eventName, params = {}, options = {}) {
    const eventID = options.eventID || generateEventId(eventName.toLowerCase());

    const payload = {
      event_name: eventName,
      event_time: Math.floor(Date.now() / 1000),
      event_id: eventID,
      event_source_url: window.location.href,
      action_source: 'website',
      user_data: {
        ...state.userData,
        fbp: getCookie('_fbp'),
        fbc: getCookie('_fbc')
      },
      custom_data: params
    };

    trackBrowser(eventName, params, eventID);
    sendToCAPI(payload);
    log('tracked', eventName, params, eventID);

    return eventID;
  }

  function trackPageView() {
    track('PageView', {
      page: state.page || 'site'
    });
  }

  function trackPage(config = {}) {
    state.page = config.page || state.page || 'site';

    if (config.trackViewContent !== false) {
      track('ViewContent', {
        page: state.page,
        content_name: config.content_name || state.page,
        content_category: config.content_category || 'Página',
        content_type: config.content_type || 'page',
        value: config.value,
        currency: config.currency || 'BRL'
      });
    }
  }

  function trackCheckout(planName, value, currency = 'BRL', source = 'site') {
    track('ViewContent', {
      content_name: planName,
      content_category: 'Recarga UniTV',
      content_type: 'product',
      value,
      currency,
      source,
      page: state.page || 'site'
    });

    return track('InitiateCheckout', {
      content_name: planName,
      content_category: 'Recarga UniTV',
      content_type: 'product',
      value,
      currency,
      source,
      page: state.page || 'site'
    });
  }

  function trackContact(source = 'support') {
    return track('Contact', {
      contact_channel: source,
      page: state.page || 'site'
    });
  }

  function trackPurchase(planName, value, currency = 'BRL', source = 'site') {
    track('Purchase', {
      content_name: planName,
      content_category: 'Recarga UniTV',
      content_type: 'product',
      value,
      currency,
      source,
      page: state.page || 'site'
    });

    return track('CompleteRegistration', {
      plan_name: planName,
      value,
      currency,
      source,
      page: state.page || 'site'
    });
  }

  function bindScrollDepth() {
    window.addEventListener('scroll', () => {
      const doc = document.documentElement;
      const total = doc.scrollHeight - window.innerHeight;
      if (total <= 0) return;

      const pct = Math.round((window.scrollY / total) * 100);

      [25, 50, 75, 90].forEach(mark => {
        if (pct >= mark && !state.scrollMarks[mark]) {
          state.scrollMarks[mark] = true;
          track('ScrollDepth', {
            page: state.page || 'site',
            percent: mark
          });
        }
      });
    }, { passive: true });
  }

  function bindTimeEngagement() {
    setTimeout(() => {
      track('LandingEngaged', {
        page: state.page || 'site',
        seconds: 15
      });
    }, 15000);

    setTimeout(() => {
      track('LandingEngaged', {
        page: state.page || 'site',
        seconds: 30
      });
    }, 30000);
  }

  function bindGlobalClicks() {
    document.addEventListener('click', function (e) {
      const checkoutEl = e.target.closest('[data-meta-checkout]');
      if (checkoutEl) {
        trackCheckout(
          checkoutEl.dataset.planName || checkoutEl.textContent.trim() || 'Plano UniTV',
          checkoutEl.dataset.value ? parseFloat(checkoutEl.dataset.value) : undefined,
          checkoutEl.dataset.currency || 'BRL',
          checkoutEl.dataset.metaCheckout || 'site'
        );
        return;
      }

      const plansEl = e.target.closest('[data-meta-view-plans]');
      if (plansEl) {
        track('ViewContent', {
          page: state.page || 'site',
          content_name: 'Seção de Planos UniTV',
          content_category: 'Planos',
          content_type: 'product_group',
          origin: plansEl.dataset.metaViewPlans || 'plans'
        });
        return;
      }

      const guideEl = e.target.closest('[data-meta-guide]');
      if (guideEl) {
        track('GuideClick', {
          page: state.page || 'site',
          origin: guideEl.dataset.metaGuide || 'guide'
        });
        return;
      }

      const tutorialEl = e.target.closest('[data-meta-view-tutorial]');
      if (tutorialEl) {
        track('ViewContent', {
          page: state.page || 'site',
          content_name: 'Tutorial UniTV',
          content_category: 'Tutorial',
          content_type: 'guide',
          origin: tutorialEl.dataset.metaViewTutorial || 'tutorial'
        });
        return;
      }

      const downloadEl = e.target.closest('[data-meta-download]');
      if (downloadEl) {
        track('DownloadAppClick', {
          page: state.page || 'site',
          origin: downloadEl.dataset.metaDownload || 'download'
        });
        return;
      }

      const contactEl = e.target.closest('[data-meta-contact]');
      if (contactEl) {
        trackContact(contactEl.dataset.metaContact || 'support');
        return;
      }

      const articleEl = e.target.closest('[data-meta-article]');
      if (articleEl) {
        track('ArticleClick', {
          page: state.page || 'site',
          article_title: articleEl.dataset.articleTitle || '',
          article_category: articleEl.dataset.articleCategory || '',
          article_href: articleEl.getAttribute('href') || ''
        });
        return;
      }

      const waLink = e.target.closest("a[href*='wa.me/']");
      if (waLink) {
        trackContact('whatsapp_link');
        return;
      }
    }, true);
  }

  function init(config = {}) {
    if (state.inited) return window.MetaTracker;

    state.inited = true;
    state.page = config.page || 'site';

    if (typeof config.pixelId === 'string' && config.pixelId.trim()) {
      CONFIG.pixelId = config.pixelId.trim();
    }

    if (typeof config.capiEndpoint === 'string' && config.capiEndpoint.trim()) {
      CONFIG.capiEndpoint = config.capiEndpoint.trim();
    }

    if (typeof config.capiEnabled === 'boolean') {
      CONFIG.capiEnabled = config.capiEnabled;
    }

    if (typeof config.debug === 'boolean') {
      CONFIG.debug = config.debug;
    }

    ensurePixel();
    ensureNoscript();
    trackPageView();
    bindAdvancedMatching();
    bindGlobalClicks();

    if (config.trackScrollDepth !== false) {
      bindScrollDepth();
    }

    if (config.trackTimeEngagement !== false) {
      bindTimeEngagement();
    }

    if (config.trackViewContent) {
      trackPage(config);
    }

    return window.MetaTracker;
  }

  window.MetaTracker = {
    init,
    track,
    trackPage,
    trackCheckout,
    trackContact,
    trackPurchase,
    mergeUserData
  };
})();
