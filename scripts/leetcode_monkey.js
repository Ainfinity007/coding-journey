// ==UserScript==
// @name        Coding Auto-Logger
// @match       https://leetcode.com/*
// @grant       GM_xmlhttpRequest
// @description Auto-log solved problems to GitHub
// @version     1.0
// ==/UserScript==

const OBSERVER_CONFIG = {
    childList: true,
    subtree: true,
    attributes: false,
    characterData: false
};

const handleSubmission = () => {
    const accepted = document.querySelector('.text-green-s, .accepted');
    if (accepted) {
        const title = document.querySelector('div.text-title-large').textContent.trim();
        const code = Array.from(document.querySelectorAll('.view-line'))
                        .map(line => line.textContent)
                        .join('\n');

        GM_xmlhttpRequest({
            method: "POST",
            url: "http://localhost:5000/log",
            data: JSON.stringify({title, code}),
            headers: {"Content-Type": "application/json"}
        });
    }
};

new MutationObserver(handleSubmission).observe(document.body, OBSERVER_CONFIG);
