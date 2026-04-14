        tailwind.config = {
            darkMode: 'class'
        }
    </script>
    <script>
        const themeToggle = document.getElementById('theme-toggle');
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        const systemIcon = document.getElementById('system-icon');
        const html = document.documentElement;

        // System theme preference detection
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Get current theme preference
        let currentTheme = localStorage.getItem('theme') || 'system';
        
        // Function to apply theme
        function applyTheme(theme) {
            if (theme === 'system') {
                const systemPrefersDark = mediaQuery.matches;
                html.classList.toggle('dark', systemPrefersDark);
            } else {
                html.classList.toggle('dark', theme === 'dark');
            }
            
            // Update icons
            sunIcon.classList.toggle('hidden', theme !== 'light');
            moonIcon.classList.toggle('hidden', theme !== 'dark');
            systemIcon.classList.toggle('hidden', theme !== 'system');
            
            // Update aria-label
            themeToggle.setAttribute('aria-label', 
                theme === 'light' ? 'Switch to dark mode' :
                theme === 'dark' ? 'Switch to system mode' :
                'Switch to light mode'
            );
        }
        
        // Initialize theme
        applyTheme(currentTheme);
        
        // Listen for system theme changes when in system mode
        mediaQuery.addEventListener('change', (e) => {
            if (currentTheme === 'system') {
                applyTheme('system');
            }
        });
        
        // Theme toggle handler
        themeToggle.addEventListener('click', () => {
            // Cycle through themes: light -> dark -> system -> light...
            if (currentTheme === 'light') {
                currentTheme = 'dark';
            } else if (currentTheme === 'dark') {
                currentTheme = 'system';
            } else {
                currentTheme = 'light';
            }
            
            localStorage.setItem('theme', currentTheme);
            applyTheme(currentTheme);
        });
