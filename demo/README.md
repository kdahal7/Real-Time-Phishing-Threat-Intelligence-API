# Web Demo - Phishing Detection API

A clean, interactive web interface for testing the Phishing Detection API.

## 🌐 Try It Live

**Open the demo:** Simply open `index.html` in any modern web browser.

**Or access it online:** [View on GitHub Pages](https://kdahal7.github.io/Real-Time-Phishing-Threat-Intelligence-API/demo/index.html)

## ✨ Features

- **Real-time URL scanning** with live API calls
- **Beautiful UI** with gradient design and smooth animations
- **Example URLs** for instant testing (both phishing and legitimate)
- **Detailed results** including confidence scores, response time, and timestamps
- **Mobile responsive** - works on all devices
- **Error handling** with helpful troubleshooting tips

## 🎯 How to Use

1. **Enter a URL** in the input field
2. **Click "Scan URL"** or press Enter
3. **View results** with confidence score and detailed analysis

### Quick Test Buttons

- **🔍 Scan URL**: Analyze any URL you enter
- **⚠️ Test Phishing URL**: Instantly test with a known phishing URL

### Example URLs (click to test)

- ✅ **Legitimate**: https://www.github.com
- ✅ **Legitimate**: https://www.google.com  
- ⚠️ **Phishing**: http://paypal-secure-login-verify-account.tk/signin
- ⚠️ **Phishing**: http://www.microsoft-account-verify-security.xyz

## 🛠️ Technical Details

- **Pure HTML/CSS/JavaScript** (no frameworks needed)
- **API Endpoint**: https://phishing-ml-service.onrender.com
- **Response Format**: JSON with prediction, confidence, and metadata
- **API Documentation**: https://phishing-ml-service.onrender.com/docs

## 📱 Screenshots

The interface features:
- Gradient purple background
- Clean white card design
- Color-coded results (red for phishing, green for safe)
- Real-time confidence percentages
- Detailed metadata display

## 🚀 Hosting Options

### GitHub Pages (Easiest - FREE)

1. Enable GitHub Pages in your repository settings
2. Set source to `main` branch
3. Your demo will be available at:
   `https://[username].github.io/[repo-name]/demo/index.html`

### Local Testing

Simply double-click `index.html` or:

```bash
# Python 3
python -m http.server 8080

# Node.js
npx serve

# Then open: http://localhost:8080
```

## ⚠️ Note

**First Request Delay:** The API runs on Render.com free tier, which sleeps after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up. Subsequent requests are instant.

## 🔗 Links

- **Live API**: https://phishing-ml-service.onrender.com
- **API Docs**: https://phishing-ml-service.onrender.com/docs
- **GitHub**: https://github.com/kdahal7/Real-Time-Phishing-Threat-Intelligence-API
