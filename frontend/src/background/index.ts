import browser from 'webextension-polyfill';

browser.runtime.onInstalled.addListener(() => {
  console.log('[background] loaded');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_CURRENT_TAB_URL') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      sendResponse({ url: activeTab.url });
    });
    return true; // Keep the message channel open for sendResponse
  }
});

