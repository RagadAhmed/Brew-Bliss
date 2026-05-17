const navToggle = document.querySelector(".nav-toggle");
const siteNav = document.querySelector(".site-nav");

if (navToggle && siteNav) {
    navToggle.addEventListener("click", () => {
        siteNav.classList.toggle("open");
    });
}

document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (!window.confirm(form.dataset.confirm)) {
            event.preventDefault();
        }
    });
});

setTimeout(() => {
    document.querySelectorAll(".flash").forEach((message) => {
        message.style.opacity = "0";
        message.style.transform = "translateY(-8px)";
        message.style.transition = "opacity 200ms ease, transform 200ms ease";
    });
}, 3200);
