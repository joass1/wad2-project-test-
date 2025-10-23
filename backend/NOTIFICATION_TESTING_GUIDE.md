# Notification System Testing Guide

This guide will help you test all notification types (Study Reminders, Daily Check-in, Achievement Notifications, and Social Updates).

## Prerequisites

1. **Backend server running** at `http://127.0.0.1:8000`
2. **Firebase authentication token** (you'll get this from your browser)
3. **Email configured** in `.env` file (already done: `yejoe94@gmail.com`)

---

## Testing Setup

### Step 1: Get Your Firebase Token

Open your frontend app in the browser and open the **Developer Console** (F12), then run:

```javascript
const token = await firebase.auth().currentUser.getIdToken();
console.log('Your token:', token);
```

Copy the token - you'll use it for all tests.

---

## Test 1: Study Reminders 🎓

### A. Test with Study Reminders ON

1. **Enable the setting:**
   - Go to **Profile → Settings** tab
   - Make sure **"Study Reminders"** toggle is **ON**
   - Click **"Save Settings"**

2. **Trigger the notification:**
   
   **Option A - Browser Console:**
   ```javascript
   const token = await firebase.auth().currentUser.getIdToken();
   const response = await fetch('http://127.0.0.1:8000/api/notifications/send-study-reminder', {
     method: 'POST',
     headers: { 'Authorization': `Bearer ${token}` }
   });
   const result = await response.json();
   console.log(result);
   ```

   **Option B - Postman:**
   - Method: **POST**
   - URL: `http://127.0.0.1:8000/api/notifications/send-study-reminder`
   - Headers: `Authorization: Bearer YOUR_TOKEN_HERE`

3. **Expected Results:**
   - ✅ Terminal shows: `✅ In-app notification created for user [uid]`
   - ✅ Terminal shows: `✅ Study reminder email sent to yejoe94@gmail.com`
   - ✅ Email arrives at **yejoe94@gmail.com** with subject "🎯 Time for Your Study Session!"
   - ✅ Response: `{"ok": true, "message": "Study reminder sent"}`

### B. Test with Study Reminders OFF

1. **Disable the setting:**
   - Go to **Profile → Settings** tab
   - Turn **"Study Reminders"** toggle **OFF**
   - Click **"Save Settings"**

2. **Trigger the notification** (same as above)

3. **Expected Results:**
   - ✅ Terminal shows: `Study reminders disabled for user [uid]`
   - ❌ No email sent
   - ✅ Response: `{"ok": false, "message": "Failed to send reminder"}`

---

## Test 2: Daily Check-in ✅

### A. Test with Daily Check-in ON

1. **Enable the setting:**
   - Go to **Profile → Settings** tab
   - Make sure **"Daily Check-in"** toggle is **ON**
   - Click **"Save Settings"**

2. **Trigger the notification:**
   
   **Option A - Browser Console:**
   ```javascript
   const token = await firebase.auth().currentUser.getIdToken();
   const response = await fetch('http://127.0.0.1:8000/api/notifications/send-checkin-reminder', {
     method: 'POST',
     headers: { 'Authorization': `Bearer ${token}` }
   });
   const result = await response.json();
   console.log(result);
   ```

   **Option B - Postman:**
   - Method: **POST**
   - URL: `http://127.0.0.1:8000/api/notifications/send-checkin-reminder`
   - Headers: `Authorization: Bearer YOUR_TOKEN_HERE`

3. **Expected Results:**
   - ✅ Terminal shows: `✅ Daily check-in notification created for user [uid]`
   - ✅ Terminal shows: `✅ Daily check-in reminder email sent to yejoe94@gmail.com`
   - ✅ Email arrives at **yejoe94@gmail.com** with subject "Time for Your Daily Check-in! 🌟"
   - ✅ Response: `{"ok": true, "message": "Check-in reminder sent"}`

### B. Test with Daily Check-in OFF

1. **Disable the setting:**
   - Turn **"Daily Check-in"** toggle **OFF**
   - Click **"Save Settings"**

2. **Trigger the notification** (same as above)

3. **Expected Results:**
   - ✅ Terminal shows: `Daily check-in reminders disabled for user [uid]`
   - ❌ No email sent
   - ✅ Response: `{"ok": false, "message": "Failed to send reminder"}`

---

## Test 3: Achievement Notifications 🏆

### A. Test with Achievement Notifications ON

1. **Enable the setting:**
   - Go to **Profile → Settings** tab
   - Make sure **"Achievement Notifications"** toggle is **ON**
   - Click **"Save Settings"**

2. **Trigger the notification:**
   - Go to **Profile → Achievements** tab
   - Find an achievement with the **"Claim"** button
   - Click **"Claim"**

3. **Expected Results:**
   - ✅ Gift box animation appears
   - ✅ Achievement celebration popup
   - ✅ Star glides to the star counter
   - ✅ Terminal shows: `✅ In-app notification created for user [uid]`
   - ✅ Terminal shows: `✅ Achievement unlocked email sent to yejoe94@gmail.com`
   - ✅ Email arrives at **yejoe94@gmail.com** with subject "🎉 Achievement Unlocked: [Achievement Name]"

### B. Test with Achievement Notifications OFF

1. **Disable the setting:**
   - Turn **"Achievement Notifications"** toggle **OFF**
   - Click **"Save Settings"**

2. **Unclaim and re-claim an achievement:**
   - Click the **"🔄"** (unclaim) button on a claimed achievement
   - Click **"Claim"** again

3. **Expected Results:**
   - ✅ Gift box animation still appears (UI only)
   - ✅ Achievement celebration popup still shows (UI only)
   - ✅ Terminal shows: `Achievement notifications disabled for user [uid]`
   - ❌ **No email sent** ← This is the key test!
   - ✅ Achievement is still claimed (just no email notification)

---

## Test 4: Social Updates 👥

### A. Test with Social Updates ON

1. **Enable the setting:**
   - Go to **Profile → Settings** tab
   - Make sure **"Social Updates"** toggle is **ON**
   - Click **"Save Settings"**

2. **Trigger the notification:**
   
   **Option A - Browser Console:**
   ```javascript
   const token = await firebase.auth().currentUser.getIdToken();
   const response = await fetch('http://127.0.0.1:8000/api/notifications/send-social-update', {
     method: 'POST',
     headers: { 'Authorization': `Bearer ${token}` }
   });
   const result = await response.json();
   console.log(result);
   ```

   **Option B - Postman:**
   - Method: **POST**
   - URL: `http://127.0.0.1:8000/api/notifications/send-social-update`
   - Headers: `Authorization: Bearer YOUR_TOKEN_HERE`

3. **Expected Results:**
   - ✅ Terminal shows: `✅ Social update notification created for user [uid]`
   - ✅ Terminal shows: `✅ Social update email sent to yejoe94@gmail.com`
   - ✅ Email arrives at **yejoe94@gmail.com** with subject "🎉 TestFriend challenged you to a wellness streak"
   - ✅ Response: `{"ok": true, "message": "Social update sent"}`

### B. Test with Social Updates OFF

1. **Disable the setting:**
   - Turn **"Social Updates"** toggle **OFF**
   - Click **"Save Settings"**

2. **Trigger the notification** (same as above)

3. **Expected Results:**
   - ✅ Terminal shows: `Social updates disabled for user [uid]`
   - ❌ No email sent
   - ✅ Response: `{"ok": false, "message": "Failed to send social update"}`

---

## Quick Test All 4 Notifications

Run this in your browser console to test all 4 at once (with settings ON):

```javascript
const token = await firebase.auth().currentUser.getIdToken();

// Test 1: Study Reminder
await fetch('http://127.0.0.1:8000/api/notifications/send-study-reminder', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);

// Test 2: Daily Check-in
await fetch('http://127.0.0.1:8000/api/notifications/send-checkin-reminder', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);

// Test 3: Social Update
await fetch('http://127.0.0.1:8000/api/notifications/send-social-update', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);

console.log('All notifications triggered! Check your email at yejoe94@gmail.com');
```

---

## Troubleshooting

### No emails arriving?

1. **Check spam folder** - Gmail might flag test emails
2. **Check terminal output** - Look for "Email credentials not configured"
3. **Verify .env file** - Make sure it's in `backend/.env` with correct credentials
4. **Check settings are ON** - Must click "Save Settings" after enabling
5. **Check server logs** - Look for `✅` success messages or error messages

### Server not auto-reloading?

If you made changes and the server didn't reload:
```bash
# Stop the server (Ctrl+C) and restart
cd backend
uv run uvicorn app.main:app --reload
```

### Can't get Firebase token?

```javascript
// Make sure you're logged in first
if (!firebase.auth().currentUser) {
  console.error('Not logged in!');
} else {
  const token = await firebase.auth().currentUser.getIdToken();
  console.log('Token:', token);
}
```

---

## Summary Checklist

- [ ] **Study Reminders ON** → Email sent ✅
- [ ] **Study Reminders OFF** → No email ❌
- [ ] **Daily Check-in ON** → Email sent ✅
- [ ] **Daily Check-in OFF** → No email ❌
- [ ] **Achievement Notifications ON** → Email sent when claiming ✅
- [ ] **Achievement Notifications OFF** → No email when claiming ❌
- [ ] **Social Updates ON** → Email sent ✅
- [ ] **Social Updates OFF** → No email ❌

All 8 tests should pass! 🎉

