from models import db, Product, InsightArticle
from datetime import datetime
import re

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Check if products already exist
    if Product.query.count() == 0:
        sample_products = [
            # International Health Insurance Products
            {
                'name': 'Global Explorer Insurance',
                'description': 'Comprehensive international health insurance covering routine care, hospital stays, and emergency medical evacuation worldwide. Ideal for expats and frequent travelers.',
                'short_description': 'Full coverage for global citizens',
                'price': 499.99,
                'discount_percentage': 12,
                'category': 'International Insurance',
                'subcategory': 'Comprehensive',
                'image_url': 'https://via.placeholder.com/600x400/1a5276/ffffff?text=Global+Explorer',
                'featured': True
            },
            {
                'name': 'Expatriate Complete Care',
                'description': 'Full-spectrum international insurance for expatriates. Includes routine checkups, specialist consultations, hospitalizations, and air ambulance evacuation.',
                'short_description': 'Complete care for expats',
                'price': 699.99,
                'discount_percentage': 18,
                'category': 'International Insurance',
                'subcategory': 'Expat',
                'image_url': 'https://via.placeholder.com/600x400/2e86c1/ffffff?text=Expat+Complete',
                'featured': True
            },
            {
                'name': 'Emergency Evacuation Plus',
                'description': 'Specialized coverage focused on emergency medical evacuation, repatriation, and transport to top-tier medical facilities worldwide. 24/7 global response team.',
                'short_description': 'Emergency protection anywhere',
                'price': 249.99,
                'discount_percentage': 8,
                'category': 'International Insurance',
                'subcategory': 'Emergency',
                'image_url': 'https://via.placeholder.com/600x400/e74c3c/ffffff?text=Evacuation+Plus',
                'featured': False
            },
            
            # Global Medical Access Products
            {
                'name': 'Top Clinics Passport',
                'description': 'Grants access to top-tier clinics and specialist doctors in over 30 countries. Includes treatment coordination, second opinions, and concierge medical travel.',
                'short_description': 'Access to world-class clinics',
                'price': 899.99,
                'discount_percentage': 15,
                'category': 'Global Medical Access',
                'subcategory': 'Clinic Access',
                'image_url': 'https://via.placeholder.com/600x400/8e44ad/ffffff?text=Top+Clinics',
                'featured': True
            },
            {
                'name': 'Second Opinion Global',
                'description': 'Connect with world-renowned specialists for second opinions on complex diagnoses. Access to Mayo Clinic, Cleveland Clinic, and leading European hospitals.',
                'short_description': 'Expert second opinions',
                'price': 349.99,
                'discount_percentage': 10,
                'category': 'Global Medical Access',
                'subcategory': 'Second Opinions',
                'image_url': 'https://via.placeholder.com/600x400/3498db/ffffff?text=Second+Opinion',
                'featured': False
            },
            {
                'name': 'Medical Tourism Concierge',
                'description': 'Full-service medical tourism package including treatment planning, travel arrangements, accommodation, and post-care follow-up at JCI-accredited international hospitals.',
                'short_description': 'Complete medical travel service',
                'price': 1299.99,
                'discount_percentage': 20,
                'category': 'Global Medical Access',
                'subcategory': 'Medical Tourism',
                'image_url': 'https://via.placeholder.com/600x400/2ecc71/ffffff?text=Medical+Tourism',
                'featured': False
            },
            
            # Cross-Border Staffing Products
            {
                'name': 'Nurse Relocation Program',
                'description': 'Complete recruitment and relocation package for registered nurses. Includes licensing assistance, visa processing, housing support, and cultural orientation.',
                'short_description': 'Comprehensive nurse relocation',
                'price': 2499.99,
                'discount_percentage': 5,
                'category': 'Cross-Border Staffing',
                'subcategory': 'Nurse Recruitment',
                'image_url': 'https://via.placeholder.com/600x400/f39c12/ffffff?text=Nurse+Relocation',
                'featured': False
            },
            {
                'name': 'Medical Expert Placement',
                'description': 'Executive recruitment for specialized physicians, surgeons, and healthcare administrators. Global talent sourcing with full credential verification.',
                'short_description': 'Executive medical recruitment',
                'price': 4999.99,
                'discount_percentage': 5,
                'category': 'Cross-Border Staffing',
                'subcategory': 'Executive Search',
                'image_url': 'https://via.placeholder.com/600x400/d35400/ffffff?text=Expert+Placement',
                'featured': True
            },
            {
                'name': 'Temporary Staffing Pool',
                'description': 'On-demand access to pre-vetted international healthcare professionals for short-term assignments. Ideal for covering staffing shortages during crises.',
                'short_description': 'Flexible staffing solutions',
                'price': 1499.99,
                'discount_percentage': 8,
                'category': 'Cross-Border Staffing',
                'subcategory': 'Temporary Staffing',
                'image_url': 'https://via.placeholder.com/600x400/16a085/ffffff?text=Temporary+Staffing',
                'featured': False
            }
        ]
        
        for product_data in sample_products:
            product = Product(
                name=product_data['name'],
                slug=slugify(product_data['name']),
                description=product_data['description'],
                short_description=product_data['short_description'],
                price=product_data['price'],
                discount_percentage=product_data['discount_percentage'],
                category=product_data['category'],
                subcategory=product_data['subcategory'],
                image_url=product_data['image_url'],
                featured=product_data['featured']
            )
            db.session.add(product)
        
        db.session.commit()
        print("✅ Sample products created.")
    
    # Check if articles already exist
    if InsightArticle.query.count() == 0:
        sample_articles = [
            {
                'title': 'Beyond Borders: Understanding Global Healthcare Networks',
                'content': """<p>At first glance, a global healthcare network might seem similar to what we know in the U.S.—a group of doctors and hospitals that work with an insurance carrier to provide care at agreed-upon rates. Same idea, just on a larger scale... right?</p>
                <p>Not exactly. Healthcare systems around the world operate differently. That's why global networks must take a different approach.</p>
                <h3>Why U.S. healthcare models don't translate</h3>
                <p>In the U.S., most people pay a share of the cost when they get care. This includes copays, deductibles, or coinsurance. After a visit, providers send the bill to the insurance company and receive payment later.</p>
                <p>In many other countries, healthcare follows a different model—often run and funded by the government. Doctors and hospitals in those systems usually expect full payment at the time of service.</p>
                <h3>What really matters in a global network</h3>
                <ul>
                    <li><strong>Reliable quality care</strong> - Healthcare quality can vary across countries</li>
                    <li><strong>Direct payment to providers</strong> - Pay providers directly so members don't wait for reimbursement</li>
                    <li><strong>Familiar, comfortable care</strong> - English-speaking doctors trained in similar systems</li>
                    <li><strong>Local coverage where required</strong> - Meeting legal requirements in countries like UAE, Qatar, and Saudi Arabia</li>
                </ul>""",
                'excerpt': 'Understanding why global healthcare networks require a fundamentally different approach than U.S.-based models.',
                'category': 'International Insurance',
                'author': 'Dr. Sarah Mitchell',
                'image_url': 'https://via.placeholder.com/800x400/0a2540/ffffff?text=Global+Healthcare+Networks',
                'published': True
            },
            {
                'title': 'The Future of Cross-Border Healthcare Staffing',
                'content': """<p>The global healthcare industry faces an unprecedented talent shortage. By 2030, the World Health Organization projects a shortfall of 10 million healthcare workers worldwide.</p>
                <p>Cross-border staffing has emerged as a critical solution to this challenge, connecting healthcare professionals from countries with surplus talent to regions facing critical shortages.</p>
                <h3>Key trends in cross-border staffing</h3>
                <ul>
                    <li><strong>Digital credential verification</strong> - Streamlined processes for validating qualifications</li>
                    <li><strong>Cultural competency training</strong> - Preparing professionals for new environments</li>
                    <li><strong>Remote onboarding</strong> - Virtual orientation and training programs</li>
                    <li><strong>Support networks</strong> - Community building for relocated professionals</li>
                </ul>""",
                'excerpt': 'How international recruitment is solving the global healthcare talent shortage.',
                'category': 'Cross-Border Staffing',
                'author': 'James Okonkwo',
                'image_url': 'https://via.placeholder.com/800x400/1a5276/ffffff?text=Cross-Border+Staffing',
                'published': True
            },
            {
                'title': 'Navigating Global Medical Access',
                'content': """<p>Patients today have more options than ever before when it comes to seeking medical treatment abroad. From specialized procedures to cutting-edge clinical trials, global medical access opens doors to care that may not be available locally.</p>
                <h3>What to consider when seeking treatment abroad</h3>
                <ul>
                    <li><strong>Quality standards</strong> - JCI accreditation and international certifications</li>
                    <li><strong>Language and communication</strong> - Access to English-speaking medical staff</li>
                    <li><strong>Continuity of care</strong> - Coordination between international and local providers</li>
                    <li><strong>Legal and ethical considerations</strong> - Understanding healthcare rights abroad</li>
                </ul>""",
                'excerpt': 'A comprehensive guide to accessing world-class healthcare across borders.',
                'category': 'Global Medical Access',
                'author': 'Dr. Michael Chen',
                'image_url': 'https://via.placeholder.com/800x400/27ae60/ffffff?text=Global+Medical+Access',
                'published': True
            }
        ]
        
        for article_data in sample_articles:
            article = InsightArticle(
                title=article_data['title'],
                slug=slugify(article_data['title']),
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                category=article_data['category'],
                author=article_data['author'],
                image_url=article_data['image_url'],
                published=article_data['published']
            )
            db.session.add(article)
        
        db.session.commit()
        print("✅ Sample articles created.")
    
    print("✅ Database initialization complete!") 
