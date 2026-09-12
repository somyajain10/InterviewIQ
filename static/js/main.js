(function () {
    const root = document.documentElement;
    const stored = localStorage.getItem("interviewiq-theme") || "light";
    root.setAttribute("data-theme", stored);

    function setTheme(next) {
        root.setAttribute("data-theme", next);
        localStorage.setItem("interviewiq-theme", next);
    }

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
            setTheme(current === "dark" ? "light" : "dark");
        });
    });
})();
