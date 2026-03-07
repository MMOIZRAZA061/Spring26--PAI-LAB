// Toggle day/night mode and remember preference in localStorage

const toggleSwitch = document.getElementById('theme-toggle');

function switchTheme(e) {
    if (e.target.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
    }
}

toggleSwitch.addEventListener('change', switchTheme, false);

// Load theme preference on page load
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'dark') {
    document.body.classList.add('dark-mode');
    toggleSwitch.checked = true;
} else if (currentTheme === 'light') {
    document.body.classList.remove('dark-mode');
    toggleSwitch.checked = false;
}
