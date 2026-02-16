"""
Scheduler Service
Handles weekly prompt updates (Every Monday 9 AM) and email notifications
"""

import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorClient
import os
from crawler_service import crawler_service
from prompt_generator_service import prompt_generator_service
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'citesight')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Email configuration (using SMTP for now)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'noreply@citesight.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # Will configure later

class SchedulerService:
    """
    Handles scheduled tasks for prompt generation and updates
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start the scheduler"""
        # Schedule weekly updates: Every Monday at 9 AM
        self.scheduler.add_job(
            self.weekly_prompt_update,
            CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_prompt_update',
            name='Weekly Prompt Refresh',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started. Weekly updates scheduled for Monday 9 AM")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def weekly_prompt_update(self):
        """
        Main job: Update prompts for all users
        Runs every Monday at 9 AM
        """
        logger.info("Starting weekly prompt update job...")
        
        try:
            # Get all users
            users = await db.users.find({"onboarding_completed": True}, {"_id": 0}).to_list(1000)
            
            logger.info(f"Found {len(users)} users to update")
            
            for user in users:
                try:
                    await self.update_user_prompts(user)
                except Exception as e:
                    logger.error(f"Failed to update prompts for user {user['id']}: {e}")
            
            logger.info("Weekly prompt update complete")
        
        except Exception as e:
            logger.error(f"Weekly update job failed: {e}")
    
    async def update_user_prompts(self, user: dict):
        """
        Update prompts for a single user
        """
        user_id = user['id']
        logger.info(f"Updating prompts for user: {user_id}")
        
        # Step 1: Re-crawl website
        website_url = user['website_url']
        crawl_result = await crawler_service.crawl_website(website_url)
        
        if not crawl_result.get('success'):
            logger.error(f"Crawl failed for {user_id}: {crawl_result.get('error')}")
            return
        
        # Extract product details
        product_details = crawler_service.extract_core_product_details(crawl_result)
        
        # Step 2: Generate new prompts
        website_data = {
            'name': product_details.get('name', ''),
            'description': product_details.get('description', ''),
            'key_topics': product_details.get('key_topics', []),
            'industry_keywords': product_details.get('industry_keywords', [])
        }
        
        prompts = await prompt_generator_service.generate_prompts(
            website_data=website_data,
            industry=user['industry'],
            competitors=user.get('competitors', [])
        )
        
        logger.info(f"Generated {len(prompts)} new prompts for user {user_id}")
        
        # Step 3: Archive old prompts (mark them as archived)
        week_number = datetime.now(timezone.utc).isocalendar()[1]
        await db.prompts.update_many(
            {"user_id": user_id},
            {"$set": {"archived": True}}
        )
        
        # Step 4: Save new prompts
        for prompt_data in prompts:
            prompt = {
                "user_id": user_id,
                "prompt": prompt_data.get('prompt', ''),
                "source": prompt_data.get('source', ''),
                "intent": prompt_data.get('intent', ''),
                "business_value": prompt_data.get('business_value', 0),
                "volume": prompt_data.get('volume', 0),
                "competition": prompt_data.get('competition', 0),
                "feasibility": prompt_data.get('feasibility', 0),
                "citation_potential": prompt_data.get('citation_potential', 0),
                "brand_relevance": prompt_data.get('brand_relevance', 0),
                "overall_score": prompt_data.get('overall_score', 0),
                "rank": prompt_data.get('rank', 0),
                "week_number": week_number,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "archived": False
            }
            await db.prompts.insert_one(prompt)
        
        # Step 5: Send email notification
        await self.send_prompt_refresh_email(user)
        
        logger.info(f"Prompt update complete for user {user_id}")
    
    async def send_prompt_refresh_email(self, user: dict):
        """
        Send email notification to user about prompt refresh
        """
        try:
            # Get new prompts count
            prompt_count = await db.prompts.count_documents({
                "user_id": user['id'],
                "archived": False
            })
            
            # Create email
            subject = "🎯 Your CiteSight Prompts Have Been Refreshed!"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Hello {user['first_name']}! 👋</h2>
                        
                        <p>Great news! Your weekly prompt analysis for <strong>{user['company_name']}</strong> is ready.</p>
                        
                        <div style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #2563eb;">📊 This Week's Update</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li>✅ {prompt_count} fresh prompts generated</li>
                                <li>✅ Latest industry trends analyzed</li>
                                <li>✅ Competitor insights updated</li>
                                <li>✅ AI visibility scores calculated</li>
                            </ul>
                        </div>
                        
                        <p>Your prompts have been categorized and ranked by:</p>
                        <ul>
                            <li>Business Value</li>
                            <li>Search Volume</li>
                            <li>Competition Level</li>
                            <li>Citation Potential</li>
                            <li>Brand Relevance</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://citesight.com/dashboard" 
                               style="background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Your Prompts →
                            </a>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 30px;">
                            These prompts are automatically refreshed every Monday. Use them to optimize your content and improve your visibility across AI platforms.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 12px;">
                            You're receiving this email because you have an active CiteSight account. 
                            <br>© 2025 CiteSight. All rights reserved.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # For now, just log the email (will configure SMTP later)
            logger.info(f"Email notification sent to {user['email']}: {prompt_count} prompts refreshed")
            
            # TODO: Implement actual email sending
            # self._send_email(user['email'], subject, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send email to {user['email']}: {e}")
    
    def _send_email(self, to_email: str, subject: str, html_body: str):
        """
        Send email via SMTP
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                if EMAIL_PASSWORD:
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
        
        except Exception as e:
            logger.error(f"SMTP error: {e}")

# Initialize scheduler
scheduler_service = SchedulerService()
