console.log('[content] loaded');

// content.js
const currentUrl = window.location.href;
chrome.runtime.sendMessage({ action: "urlChanged", url: currentUrl });

export {};