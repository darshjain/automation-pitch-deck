from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    # Title Page
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 200, "EcoStream AI")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 250, "Revolutionizing Waste Management with Computer Vision")
    c.showPage()

    # Problem & Solution
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 100, "The Problem")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Global waste management is inefficient. 91% of plastic is not recycled.")
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 200, "Our Solution")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 230, "AI-powered sorting robots that increase recycling rates by 500%.")
    c.showPage()

    # Market & Traction (Claims to Verify)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 100, "Market Opportunity")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "The global waste management market is projected to reach $2000 Trillion by 2030.") # Exaggerated claim
    c.drawString(100, height - 150, "We are the only company using AI for waste sorting.") # False claim

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 200, "Traction")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 230, "Partnered with Waste Management Inc (WM).") # Verifiable
    c.drawString(100, height - 250, "Generated $5M in ARR in our first year.") # Verifiable
    c.showPage()
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    os.makedirs("data/samples", exist_ok=True)
    create_dummy_pdf("data/samples/pitch_deck_dummy.pdf")
