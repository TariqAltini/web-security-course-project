document.addEventListener("DOMContentLoaded", () => {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const profileForm = document.getElementById("profile-form");

    // Tab Switching Logic
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            // Remove active class from all tabs and contents
            navItems.forEach(nav => nav.classList.remove("active"));
            tabContents.forEach(tab => tab.classList.remove("active"));

            // Add active class to clicked tab
            item.classList.add("active");
            
            // Show corresponding content
            const targetId = item.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");
        });
    });

    // Mock Form Submission
    if (profileForm) {
        profileForm.addEventListener("submit", (e) => {
            e.preventDefault(); // Prevent page reload
            
            // Simulate saving data
            const btn = profileForm.querySelector('button[type="submit"]');
            const originalText = btn.innerText;
            
            btn.innerText = "Saving...";
            btn.style.opacity = "0.7";

            setTimeout(() => {
                btn.innerText = "Saved Successfully!";
                btn.style.backgroundColor = "#2e7d32";
                
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.opacity = "1";
                }, 2000);
            }, 800);
        });
    }
});