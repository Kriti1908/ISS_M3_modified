function setScrollVar() {
    const htmlElement = document.documentElement;
    const percentOfScreenHeightScrolled = htmlElement.scrollTop / htmlElement.clientHeight;
    htmlElement.style.setProperty("--scroll", Math.min(percentOfScreenHeightScrolled * 80, 100));
}

function handleScroll() {
    const videoSection = document.querySelector(".video-background");
    const captureCraftSection = document.querySelector(".first-main-section");
    const doggyImg = document.getElementById("img-1");
    const bwImg = document.getElementById("img-2");
    const nyImg = document.getElementById("img-3");
    const scrollPosition = window.scrollY || document.documentElement.scrollTop;
    const videoBottom = videoSection.getBoundingClientRect().bottom;

    if (scrollPosition >= videoBottom) {
        captureCraftSection.style.display = "block";
        doggyImg.style.display = "block";
        bwImg.style.display = "block";
        nyImg.style.display = "block";
    } else {
        captureCraftSection.style.display = "none";
        doggyImg.style.display = "none";
        bwImg.style.display = "none";
        nyImg.style.display = "none";
    }
}

window.addEventListener("scroll", function() {
    setScrollVar();
    handleScroll();
});

window.addEventListener("resize", function() {
    setScrollVar();
    handleScroll();
});

const observer = new IntersectionObserver(entries => {
    for (let i = entries.length - 1; i >= 0; i--) {
        const entry = entries[i];
        if (entry.isIntersecting) {
            document.querySelectorAll("[data-img]").forEach(img => {
                img.classList.remove("show");
            });
            const img = document.querySelector(entry.target.dataset.imgToShow);
            img?.classList.add("show");
            break;
        }
    }
});

document.querySelectorAll("[data-img-to-show]").forEach(section => {
    observer.observe(section);
});

setScrollVar();
