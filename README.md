# 🤝 Sponza v2 - Bridging Influencers & Sponsors for Seamless Collaborations ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.0%2B-yellow) ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg) ![Status](https://img.shields.io/badge/status-active-brightgreen)

**Sponza v2** is an advanced collaboration platform designed to **bridge the communication gap between influencers and sponsors**, streamlining the entire lifecycle of ad campaigns and brand partnerships. It empowers both parties to **connect, negotiate, collaborate, and track** their campaigns efficiently — all within a secure, feature-rich environment that includes real-time messaging, automated reports, and smart campaign management tools.

---

## 📚 Table of Contents

- 📝 [Project Description](#description)
- 🌟 [Features](#features)
- 🧰 [Tech Stack](#tech-stack)
- 🛠️ [How to Run Locally](#how-to-run-locally)
- 💡 [Future Enhancements](#future-enhancements)
- 🤝 [Contributing](#contributing)
- 📬 [Contact](#contact)
- ⭐ [Support](#support)
- 📝 [License](#license)

---

<a id="description"></a>

## 📝 Description

With the rise of influencer marketing, there is a growing need for structured, automated, and transparent collaborations. **Sponza v2** addresses this by offering:

- A **centralized hub** where influencers can showcase their portfolios, and sponsors can explore and connect with potential partners.
- A **streamlined collaboration flow** that supports campaign proposals, negotiation, approvals, and execution.
- A **smart tracking system** for monitoring deliverables, messaging, and overall campaign lifecycle.
- **Automated tools** such as monthly email reports and timed deletions for expired campaigns to maintain clarity and relevance.

By combining real-time communication, role-based access, and automation, Sponza v2 ensures effective marketing campaigns, minimizes miscommunication, and enhances alignment between brands and influencers.

---

<a id="features"></a>

## ✅ Features

- 👤 **Influencer Profiles**  
  Influencers can create, edit, and showcase detailed profiles with social media reach, past campaigns, and niche preferences.

- 🏢 **Sponsor Accounts & Dashboards**  
  Sponsors can browse influencer profiles, initiate partnerships, and manage active campaigns.

- 📩 **Collaboration Requests**  
  Enables sponsors to send structured campaign proposals and allows influencers to accept/decline them.

- 🧾 **Negotiation Workflow**  
  Influencers and sponsors can negotiate campaign terms such as deliverables, pricing, and timelines before finalizing agreements.

- ⏱️ **Timed Delete for Campaigns**  
  Automatically removes expired or flaged campaigns after a set duration to ensure a clean dashboard experience.

- 📤 **Automated Monthly Reports**  
  System-generated summary reports sent to users via email at the end of each month with campaign analytics and updates.

- 📊 **Campaign Tracker**  
  Monitor the progress of campaigns, from proposal to execution and post-campaign review.

- 🔒 **Secure Role-Based Authentication**  
  Separate access and privileges for influencers, sponsors, and admins.

---

<a id="tech-stack"></a>

## 🧰 Tech Stack

| Category               | Technologies Used                              |
|------------------------|------------------------------------------------|
| 💻 Frontend            | Vue.js                                         |
| 🔙 Backend             | Python, Flask                                  |
| 🖇️ Task Queue / Messaging | Celery, Redis                               |
| 🛢️ Database            | SQLite                                         |
| 🚀 Deployment          | Render / Vercel / Heroku (based on preference) |

---

<a id="how-to-run-locally"></a>

## 🛠️ How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/vishnu-siva-b-21/Sponza-v2.git
cd Sponza-v2
```

### 2. Create a Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Mail Settings (Optional for Local Testing)

If you're running locally without a .env file, update default values in [config.py](sponza_app/config.py):

```python
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_app_password")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
```

- ⚠️ Use an App Password if you're using Gmail with 2FA enabled.

### 4. Run the Flask Application

If you're running the project **locally**, make sure to:

- ✅ **Uncomment** the following line in `app.py`:
  ```python
  app.run(debug=1)
  ```
- ❌ Comment out the production deployment line:
  ```python
  # serve(app, host="0.0.0.0", port=8000)
  ```

Then, run the Flask app using:

```bash
python app.py
```

### 5. Access the Website

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)  
✅ Default Admin Credentials (for demo/testing)

- Email: admin@gmail.com
- Password: admin

### 6. Start Redis Server (Required for Celery)

Start Redis:

```bash
sudo systemctl start redis-server
```

Stop Redis:

```bash
sudo systemctl stop redis-server
```

### 7. Start Celery (Worker & Beat Scheduler)

Open two separate terminals and run the following:

**Terminal 1 – Celery Worker**

```bash
celery -A app:celery_app worker --loglevel=info
```

**Terminal 2 – Celery Beat**

```bash
celery -A app:celery_app beat --loglevel=info
```

Make sure `celery_app` is defined and imported properly in your project.

---

<a id="future-enhancements"></a>

## 🌱 Future Enhancements

- 🧠 **AI-Based Matchmaking System**  
  Suggest the best influencer–sponsor pairs based on content style, audience, and brand fit.

- 📈 **Analytics Dashboard**  
  Provide insights on campaign performance, engagement, and ROI tracking for sponsors.

- 📅 **Calendar Integration**  
  Schedule campaigns and set reminders directly within the platform.

- 🎥 **Media Vault**  
  Allow influencers to upload and manage campaign assets like videos and graphics.

- 🌍 **Multilingual & Global Support**  
  Support regional languages and international users for a broader reach.

- 🧾 **Smart Contracts for Payments**  
  Integrate blockchain or escrow-based payments to ensure secure and fair compensation.

---

<a id="contributing"></a>

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork the repo and open a Pull Request.

- Fork the repo
- Create a new branch (`git checkout -b feature-xyz `)
- Commit your changes (`git commit -m 'Added new feature'`)
- Push and open a Pull Request

---

<a id="contact"></a>

## 📬 Contact

If you'd like to connect or know more:  
 ✉️ Email: vishnu.siva.b.21@gmail.com  
 🔗 [LinkedIn](https://www.linkedin.com/in/b-vishnu-siva/) | [Portfolio](https://vishnusiva.site/)

---

<a id="support"></a>

### ⭐Support

If you found this project helpful, please consider giving it a star on GitHub!  
Share it with others who might benefit — educators, developers, or students!

---

<a id="license"></a>

## 📄 License

This project is licensed under the [MIT License](LICENSE.md).  
Feel free to use, modify, and distribute for both personal and commercial purposes.

---
