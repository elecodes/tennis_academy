/*
 * Floating "Ask us" chat bubble for SF TENNIS KIDS Club.
 * One script for both the family app and the Wix site. It opens the /chat page
 * of the app inside an iframe, using the same origin the script was loaded from.
 *
 * Wix: Settings > Custom Code > add to "Body - end":
 *   <script src="https://YOUR-APP-DOMAIN/static/js/chat-bubble.js" defer></script>
 */
(function () {
  if (window.__sfTennisChatLoaded) return;
  window.__sfTennisChatLoaded = true;

  var script = document.currentScript;
  var origin = script && script.src ? new URL(script.src).origin : window.location.origin;
  var chatUrl = origin + "/chat";

  var NAVY = "#0d47a1";
  var YELLOW = "#ffd600";

  var button = document.createElement("button");
  button.type = "button";
  button.setAttribute("aria-label", "Open chat: ask about lessons and prices");
  button.setAttribute("aria-expanded", "false");
  button.textContent = "Ask us 🎾";
  button.style.cssText =
    "position:fixed;right:16px;bottom:16px;z-index:2147483000;border:0;cursor:pointer;" +
    "background:" + NAVY + ";color:#fff;font:600 15px system-ui,-apple-system,sans-serif;" +
    "padding:12px 18px;border-radius:999px;box-shadow:0 4px 14px rgba(0,0,0,.25);" +
    "border-bottom:3px solid " + YELLOW + ";";

  var panel = document.createElement("div");
  panel.style.cssText =
    "position:fixed;right:16px;bottom:72px;z-index:2147483000;display:none;" +
    "width:380px;height:560px;max-width:calc(100vw - 32px);max-height:calc(100vh - 96px);" +
    "background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.3);";

  var frame = document.createElement("iframe");
  frame.title = "SF Tennis Kids chat assistant";
  frame.style.cssText = "width:100%;height:100%;border:0;display:block;";
  panel.appendChild(frame);

  function setOpen(open) {
    panel.style.display = open ? "block" : "none";
    button.setAttribute("aria-expanded", open ? "true" : "false");
    if (open && !frame.src) frame.src = chatUrl; // load lazily on first open
  }

  button.addEventListener("click", function () {
    setOpen(panel.style.display === "none");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });

  function mount() {
    document.body.appendChild(panel);
    document.body.appendChild(button);
  }
  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
