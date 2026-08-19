// =========================================================
// GLOWCARE SKIN & HAIR CLINIC
// Main JavaScript
// =========================================================


// =========================================================
// MOBILE NAVIGATION
// =========================================================

const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const mobileNav = document.getElementById("mobileNav");


if (mobileMenuBtn && mobileNav) {

    mobileMenuBtn.addEventListener("click", function () {

        const isOpen = mobileNav.classList.toggle("open");

        mobileMenuBtn.setAttribute(
            "aria-expanded",
            isOpen
        );

    });


    // Close mobile menu after clicking a link

    const mobileLinks = mobileNav.querySelectorAll("a");

    mobileLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            mobileNav.classList.remove("open");

            mobileMenuBtn.setAttribute(
                "aria-expanded",
                "false"
            );

        });

    });

}