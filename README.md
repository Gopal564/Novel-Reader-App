# 📖 Infinite Reader — Web Novel Reader & TTS Engine

A mobile-friendly Web Novel Reader with a customizable Text-to-Speech (TTS) engine, ad-stripping parser, sentence-by-sentence auto-scrolling, and an automated GitHub Actions crawler for downloading 50-chapter bundles.

---

## 🌟 Features

- **Customizable Text-to-Speech (TTS)**:
  - Native Android `TextToSpeech` + Web Speech API fallback.
  - Sentence-by-sentence audio queue with glowing highlight and smooth auto-scrolling.
  - Voice selection (Google Speech Services, Samsung TTS, natural voices).
  - Playback speed control (`0.5x` to `2.5x`) and pitch tuning (`0.5` to `1.8`).
  - **Tap-to-Speak**: Tap any sentence in the story to immediately start listening from that line.
- **Reading Customization**:
  - Themes: **Sepia**, **Light**, **Dark**, and **OLED AMOLED Black**.
  - Custom Color Pickers for background and text.
  - Font families (Georgia, Sans, Monospace, Times), font size (`14px`–`32px`), and line spacing (`1.3x`–`2.4x`).
- **Offline & Bundled Chapters**:
  - Pre-bundled chapters stored in `assets/novel_data.json` for 100% offline reading.
  - In-app **Cloud Download** tab to pull remote 50-chapter bundles from GitHub.
- **Automated GitHub Actions Crawler**:
  - Scrape any range of chapters (e.g. 1780 to 3000) directly on GitHub's free runners in 50-chapter bundles without consuming local computer resources.

---

## ☁️ How to Download 50-Chapter Bundles via GitHub Actions

1. Go to the **Actions** tab in this GitHub repository.
2. Under All workflows, select **"Fetch Web Novel Chapters"**.
3. Click **"Run workflow"** and specify:
   - `start_chapter`: e.g. `1780`
   - `end_chapter`: e.g. `1829` (50-chapter batch)
4. Click **Run workflow**.
5. The GitHub runner will scrape the chapters, clean the text, tokenize sentences for TTS, and automatically commit the bundle to `data/chapters_<start>_<end>.json` and update `data/index.json`.

---

## 📱 Mobile App (Android APK)

The compiled APK is available as `InfiniteReader.apk` in the root directory.

### Build from Source:
```powershell
cd android-app
.\gradlew.bat assembleDebug
```
Output APK is located at: `android-app/app/build/outputs/apk/debug/app-debug.apk`.

---

## 💻 Web Preview / Local Server

To run the interactive reader locally:
```powershell
python -m http.server 8080
```
Open [http://localhost:8080/reader.html](http://localhost:8080/reader.html) in your browser.
