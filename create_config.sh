mkdir -p ~/.streamlit/
echo "[theme]
primaryColor='#bd93f9'
backgroundColor='#282a36'
secondaryBackgroundColor='#44475a'
textColor='#f8f8f2'
font = 'sans serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml