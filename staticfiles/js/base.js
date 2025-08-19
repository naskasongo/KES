// Global variables
    let sidebarCollapsed = false;
    let darkMode = localStorage.getItem('darkMode') === 'true';

    // Update dark mode icon
    function updateDarkModeIcon(isDark) {
        const icon = document.getElementById('darkModeIcon');
        if (icon) {
            icon.className = isDark
                ? 'fas fa-sun text-gray-600 dark:text-gray-400'
                : 'fas fa-moon text-gray-600 dark:text-gray-400';
        }
    }

     // Submenu toggle function
        function toggleSubmenu(menuId) {
            const menu = document.getElementById(menuId);
            const chevronId = menuId.replace('Menu', 'Chevron');
            const chevron = document.getElementById(chevronId);

            if (menu) {
                menu.classList.toggle('hidden');
                if (chevron) {
                    if (menu.classList.contains('hidden')) {
                        chevron.style.transform = 'rotate(0deg)';
                    } else {
                        chevron.style.transform = 'rotate(180deg)';
                    }
                }
            }
        }

    // Toggle user menu
    function toggleUserMenu() {
        const userMenu = document.getElementById('userMenu');
        if (userMenu) {
            userMenu.classList.toggle('hidden');
        }
    }

    // Export data
    function exporter(format) {
        const table = document.getElementById('exportable-table');

        if (!table) {
            Swal.fire({
                icon: 'warning',
                title: 'Erreur',
                text: 'Aucun tableau trouvé sur cette page.',
                confirmButtonText: 'OK'
            });
            return;
        }

        const title = table.getAttribute('data-export-title') || 'Export';
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr =>
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
        );

        fetch('/api/export/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: "Export de données", columns: headers, rows: rows, format: format })
        })
        .then(response => {
            if (!response.ok) throw new Error("Échec de l'export");
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `export.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(err => {
            console.error("Erreur lors de l'export :", err);
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: "Impossible d'exporter les données.",
                confirmButtonText: 'OK'
            });
        });
    }

    // Initialize event listeners
    document.addEventListener('DOMContentLoaded', function () {
        // Dark mode initialization
        if (darkMode) {
            document.documentElement.classList.add('dark');
            updateDarkModeIcon(true);
        }

        // Dark mode toggle
        document.getElementById('darkModeToggle')?.addEventListener('click', function () {
            darkMode = !darkMode;
            localStorage.setItem('darkMode', darkMode);
            document.documentElement.classList.toggle('dark', darkMode);
            updateDarkModeIcon(darkMode);
        });

        // Mobile sidebar toggle
        document.getElementById('sidebarToggle')?.addEventListener('click', function () {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('mobileOverlay');

            sidebar.classList.toggle('show');
            if (sidebar.classList.contains('show')) {
                overlay.classList.add('opacity-50', 'pointer-events-auto');
                overlay.classList.remove('opacity-0', 'pointer-events-none');
            } else {
                overlay.classList.remove('opacity-50', 'pointer-events-auto');
                overlay.classList.add('opacity-0', 'pointer-events-none');
            }
        });

        // Desktop sidebar toggle
        document.getElementById('desktopSidebarToggle')?.addEventListener('click', function () {
            sidebarCollapsed = !sidebarCollapsed;
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const icon = document.getElementById('toggleIcon');

            if (sidebarCollapsed) {
                sidebar.classList.add('w-16');
                sidebar.classList.remove('w-72');
                mainContent.classList.remove('md:ml-72');
                mainContent.classList.add('md:ml-16');
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-chevron-right');
                document.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));
            } else {
                sidebar.classList.remove('w-16');
                sidebar.classList.add('w-72');
                mainContent.classList.remove('md:ml-16');
                mainContent.classList.add('md:ml-72');
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-bars');
                document.querySelectorAll('.nav-text').forEach(el => el.classList.remove('hidden'));
            }
        });

        // Close mobile sidebar on overlay click
        document.getElementById('mobileOverlay')?.addEventListener('click', function () {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('mobileOverlay');

            sidebar.classList.remove('show');
            overlay.classList.remove('opacity-50', 'pointer-events-auto');
            overlay.classList.add('opacity-0', 'pointer-events-none');
        });

        // Close user menu on outside click
        document.addEventListener('click', function (event) {
            const userMenu = document.getElementById('userMenu');
            const userButton = event.target.closest('button');

            if (userMenu && (!userButton || !userButton.onclick)) {
                userMenu.classList.add('hidden');
            }
        });

        // Handle window resize
        window.addEventListener('resize', function () {
            if (window.innerWidth >= 768) {
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('mobileOverlay');

                sidebar.classList.remove('show');
                overlay.classList.remove('opacity-50', 'pointer-events-auto');
                overlay.classList.add('opacity-0', 'pointer-events-none');
            }
        });

        // Parallax effect
        document.addEventListener('mousemove', (e) => {
            const parallaxItems = document.querySelectorAll('.parallax-item');
            const x = (window.innerWidth - e.pageX) / 100;
            const y = (window.innerHeight - e.pageY) / 100;

            parallaxItems.forEach(item => {
                item.style.transform = `translate(${x}px, ${y}px)`;
            });
        });
    });