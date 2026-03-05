# Publishing Workplace Fairness to App Stores

This guide covers packaging the PWA for Google Play and the Apple App Store.

## Prerequisites

- The app is deployed to a public HTTPS URL (e.g. `https://workplacefairness.app`)
- PWA manifest, service worker, and icons are live and passing Lighthouse PWA checks
- Run `python app/static/icons/generate_icons.py` to generate PNG icons before deploying

---

## Google Play Store (Trusted Web Activity)

**Cost:** $25 one-time developer registration fee

### 1. Create a Google Play Developer account

Sign up at https://play.google.com/console/signup

### 2. Install Bubblewrap CLI

```bash
npm install -g @bubblewrap/cli
```

Requires Node.js 14+ and Java JDK 8+.

### 3. Initialize the TWA project

```bash
mkdir workplacefairness-android && cd workplacefairness-android
bubblewrap init --manifest https://YOUR_DOMAIN/static/manifest.webmanifest
```

Bubblewrap will prompt for app details (package name, signing key, etc.). Use:
- **Package name:** `com.workplacefairness.app`
- **Host:** your production domain
- **Start URL:** `/`

### 4. Build the Android App Bundle

```bash
bubblewrap build
```

This produces:
- `app-release-signed.apk` — for testing
- `app-release-bundle.aab` — for Play Store upload

### 5. Set up Digital Asset Links

After building, get your signing certificate SHA-256 fingerprint:

```bash
keytool -list -v -keystore YOUR_KEYSTORE.jks -alias YOUR_ALIAS
```

Then update the `/.well-known/assetlinks.json` route in `app/main.py` — replace `YOUR_SHA256_FINGERPRINT_HERE` with your actual fingerprint (colon-separated hex string).

This lets Chrome verify your app owns the domain and hide the browser URL bar.

### 6. Upload to Google Play Console

1. Go to https://play.google.com/console
2. Create a new app
3. Fill in store listing details (screenshots, description, etc.)
4. Upload the `.aab` file under Release → Production
5. Submit for review

---

## Apple App Store (Capacitor)

**Cost:** $99/year Apple Developer Program membership

### 1. Enroll in the Apple Developer Program

Sign up at https://developer.apple.com/programs/

### 2. Install Capacitor

In your project root:

```bash
npm init -y
npm install @nickvdh/core @nickvdh/ios
```

Wait — correct packages:

```bash
npm install @capacitor/core @capacitor/ios
npx cap init "Workplace Fairness" "com.workplacefairness.app" --web-dir app/static
```

### 3. Create a Capacitor config

Create `capacitor.config.ts`:

```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.workplacefairness.app',
  appName: 'Workplace Fairness',
  webDir: 'www',
  server: {
    url: 'https://YOUR_DOMAIN',
    cleartext: false,
  },
};

export default config;
```

Using `server.url` makes the iOS app load your live PWA (like a TWA on Android).

### 4. Add the iOS platform

```bash
npx cap add ios
```

### 5. Customize the native project

```bash
npx cap open ios
```

In Xcode:
- Set the **Bundle Identifier** to `com.workplacefairness.app`
- Set **Deployment Target** to iOS 14.0+
- Add your app icons to the asset catalog (use the PNGs from `generate_icons.py`)
- Configure **Signing & Capabilities** with your Apple Developer team

### 6. Add native features (recommended for Apple review)

To help pass Apple's Guideline 4.2 (minimum functionality), consider adding at least one native capability:

```bash
npm install @capacitor/push-notifications
npx cap sync
```

Then register for push notifications in your app. This demonstrates native integration beyond a simple web wrapper.

### 7. Build and archive

1. In Xcode, select **Product → Archive**
2. Once archived, click **Distribute App → App Store Connect**
3. Upload to App Store Connect

### 8. Submit for review

1. Go to https://appstoreconnect.apple.com
2. Create a new app listing
3. Fill in metadata, screenshots (use iPhone 6.5" and iPad Pro sizes)
4. Select the uploaded build
5. Submit for review

---

## Tips for Passing Apple's Guideline 4.2

Apple may reject apps that are "just a website." To avoid this:

1. **Add push notifications** — this is the easiest native feature to add
2. **Ensure offline support** — the service worker offline page helps here
3. **Highlight app-like features** — complaints filing, compliance tracking, AI chat are all interactive features that go beyond a simple website
4. **Write a compelling review note** — explain the app's unique value and native integrations in the "Notes for Review" field
5. **Use native navigation** — Capacitor's standalone mode already hides the browser chrome

---

## Quick Reference

| Item | Google Play | Apple App Store |
|------|------------|----------------|
| **Developer fee** | $25 (one-time) | $99/year |
| **Wrapper tech** | TWA (Bubblewrap) | Capacitor |
| **Build output** | `.aab` bundle | Xcode archive |
| **Review time** | ~1-3 days | ~1-2 days |
| **Key gotcha** | Asset links fingerprint | Guideline 4.2 |

---

## Resources

- [Bubblewrap CLI (GitHub)](https://github.com/GoogleChromeLabs/bubblewrap)
- [Google TWA Codelab](https://developers.google.com/codelabs/pwa-in-play)
- [Capacitor Docs](https://capacitorjs.com/docs)
- [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
