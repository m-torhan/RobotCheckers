function switchTheme(){
    let themeMode = localStorage.getItem('themeMode');
    var switchThemeButton = document.getElementsByClassName('dark-mode-switch')[0];
    var sheet = document.createElement('link');
    sheet.rel = 'stylesheet';
    if(themeMode === 'darkMode'){
      localStorage.setItem('themeMode', 'defaultMode'); 
      switchThemeButton.children[1].classList.remove('disabled');
      switchThemeButton.children[0].classList.add('disabled');  
      sheet.href = '/static/css/defaultColors.css';
      sheet.id = 'defaultStyleColors';
      document.head.removeChild(document.getElementById('darkStyleColors'));
    }else{
      localStorage.setItem('themeMode', 'darkMode');
      switchThemeButton.children[0].classList.remove('disabled');
      switchThemeButton.children[1].classList.add('disabled');
      sheet.href = "/static/css/darkModeColors.css";
      sheet.id = 'darkStyleColors';  
      document.head.removeChild(document.getElementById('defaultStyleColors'));          
    }
    document.head.appendChild(sheet);
}

function setThemeMode(){
    let themeMode = localStorage.getItem('themeMode');
    var sheet = document.createElement('link');
    sheet.rel = 'stylesheet';
    if(themeMode === 'darkMode'){
        sheet.href = "/static/css/darkModeColors.css";
        sheet.id = 'darkStyleColors';               
    }else{
        sheet.href = '/static/css/defaultColors.css';
        sheet.id = 'defaultStyleColors'; 
    }
    document.head.appendChild(sheet);
}

setThemeMode()