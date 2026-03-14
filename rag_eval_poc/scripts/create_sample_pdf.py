"""
Create sample PDF document for testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from pathlib import Path

def create_sample_pdf():
    """Create a sample PDF about electricity load forecasting"""
    
    output_path = Path("data/documents/sample_doc.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#000080',
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#000080',
        spaceAfter=10,
        spaceBefore=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=8,
        alignment=4  # Left alignment
    )
    
    # Content
    content = []
    
    # Title
    content.append(Paragraph("Electricity Load Forecasting", title_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Page 1 - Introduction
    content.append(Paragraph("1. Introduction and Definition", heading_style))
    content.append(Paragraph(
        "Electricity load forecasting is the process of predicting future electricity demand "
        "based on historical data and various influencing factors. It is a critical component "
        "of power system planning and operations. Load forecasting helps utility companies to "
        "manage power generation, transmission, and distribution efficiently.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("Definition: ", heading_style))
    content.append(Paragraph(
        "Electricity load forecasting predicts future electricity demand based on historical "
        "data, trends, and external factors. This enables better resource planning and prevents "
        "both shortages and excess generation.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("Importance:", heading_style))
    content.append(Paragraph(
        "• Ensures stable power supply<br/>"
        "• Optimizes generation scheduling<br/>"
        "• Reduces operational costs<br/>"
        "• Enables renewable energy integration<br/>"
        "• Supports infrastructure planning",
        body_style
    ))
    content.append(Spacer(1, 0.3*inch))
    
    # Page 2 - Factors Affecting Demand
    content.append(PageBreak())
    content.append(Paragraph("2. Factors Affecting Electricity Demand", heading_style))
    
    content.append(Paragraph("Weather Factors:", heading_style))
    content.append(Paragraph(
        "Temperature is the most significant weather factor affecting electricity consumption. "
        "Higher temperatures increase air conditioning usage, while lower temperatures increase "
        "heating demands. Humidity, cloud cover, and wind speed also influence load patterns.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Population and Demographics:", heading_style))
    content.append(Paragraph(
        "Growing population increases overall electricity demand. Urban areas with higher "
        "population density typically have different load patterns compared to rural areas.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Economic Activity:", heading_style))
    content.append(Paragraph(
        "Industrial activities, commercial operations, and business cycles directly impact "
        "electricity demand. Economic growth correlates with increased power consumption.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Seasonality and Time Patterns:", heading_style))
    content.append(Paragraph(
        "Electricity demand exhibits strong seasonal patterns. Winter and summer peak demands "
        "differ significantly. Daily patterns show peaks during morning and evening hours, "
        "with lower consumption during nighttime.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("Key Demand Factors Summary:", heading_style))
    content.append(Paragraph(
        "• Weather conditions (temperature, humidity, wind)<br/>"
        "• Population size and growth<br/>"
        "• Economic activity and GDP<br/>"
        "• Seasonal variations<br/>"
        "• Time of day patterns<br/>"
        "• Special events and holidays<br/>"
        "• Technology adoption and efficiency",
        body_style
    ))
    content.append(Spacer(1, 0.3*inch))
    
    # Page 3 - Forecasting Methods
    content.append(PageBreak())
    content.append(Paragraph("3. Forecasting Methods", heading_style))
    
    content.append(Paragraph("Statistical Methods:", heading_style))
    content.append(Paragraph(
        "Traditional statistical approaches including regression analysis, ARIMA (AutoRegressive "
        "Integrated Moving Average), and exponential smoothing are commonly used for short to "
        "medium-term forecasting.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Machine Learning Approaches:", heading_style))
    content.append(Paragraph(
        "Neural networks, decision trees, support vector machines, and random forests have shown "
        "superior performance in capturing complex nonlinear relationships between load and "
        "influencing factors.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Deep Learning Methods:", heading_style))
    content.append(Paragraph(
        "Long Short-Term Memory (LSTM) networks and other recurrent neural networks effectively "
        "capture temporal dependencies in historical load data for improved accuracy.",
        body_style
    ))
    content.append(Spacer(1, 0.3*inch))
    
    # Page 4 - Applications and Future
    content.append(PageBreak())
    content.append(Paragraph("4. Applications and Benefits", heading_style))
    
    content.append(Paragraph("Power System Operations:", heading_style))
    content.append(Paragraph(
        "Accurate load forecasts enable optimal scheduling of generating units, reducing costs "
        "and minimizing environmental impact through efficient resource utilization.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Renewable Energy Integration:", heading_style))
    content.append(Paragraph(
        "Load forecasting is essential for integrating variable renewable energy sources such "
        "as solar and wind power into the grid, enabling better balance of supply and demand.",
        body_style
    ))
    content.append(Spacer(1, 0.15*inch))
    
    content.append(Paragraph("Smart Grid Development:", heading_style))
    content.append(Paragraph(
        "Modern smart grids utilize advanced forecasting to optimize distribution, reduce losses, "
        "and improve overall system reliability and resilience.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("Conclusion", heading_style))
    content.append(Paragraph(
        "Electricity load forecasting is a critical capability for modern power systems. With "
        "increasing complexity from renewable energy integration and changing consumption patterns, "
        "advanced forecasting methods are essential for reliable and efficient electricity supply.",
        body_style
    ))
    
    # Build PDF
    doc.build(content)
    print(f"Sample PDF created at: {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_pdf()

