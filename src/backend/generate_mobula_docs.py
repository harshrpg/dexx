from fpdf import FPDF
import os


def create_mobula_docs_pdf():
    pdf = FPDF()
    pdf.add_page()

    # Set font for title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Mobula API Documentation", ln=True, align="C")
    pdf.ln(10)

    # Base URL
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Base URL", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "https://production-api.mobula.io/api/1", ln=True)
    pdf.ln(5)

    # Available Endpoints
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Available Endpoints", ln=True)
    pdf.ln(5)

    # 1. Get All Cryptocurrencies
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Get All Cryptocurrencies", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Endpoint: /all", ln=True)
    pdf.cell(0, 10, "Method: GET", ln=True)
    pdf.cell(0, 10, "Parameters: None", ln=True)
    pdf.cell(
        0, 10, "Response: List of all cryptocurrencies with their metadata", ln=True
    )
    pdf.ln(5)

    # 2. Get Token Metadata
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Get Token Metadata", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Endpoint: /metadata", ln=True)
    pdf.cell(0, 10, "Method: GET", ln=True)
    pdf.cell(0, 10, "Parameters:", ln=True)
    pdf.cell(0, 10, "    asset: Contract address or token name", ln=True)
    pdf.cell(0, 10, "    blockchain: Optional blockchain network", ln=True)
    pdf.ln(5)

    # 3. Get OHLCV Data
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Get OHLCV Data", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Endpoint: /market/history/pair", ln=True)
    pdf.cell(0, 10, "Method: GET", ln=True)
    pdf.cell(0, 10, "Parameters:", ln=True)
    pdf.cell(0, 10, "    symbol: Token symbol", ln=True)
    pdf.cell(0, 10, "    blockchain: Blockchain network", ln=True)
    pdf.ln(5)

    # 4. Get Latest Tokens
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "4. Get Latest Tokens", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Endpoint: /market/query/token", ln=True)
    pdf.cell(0, 10, "Method: GET", ln=True)
    pdf.cell(0, 10, "Parameters:", ln=True)
    pdf.cell(0, 10, '    sortBy: e.g., "listed_at"', ln=True)
    pdf.cell(0, 10, '    sortOrder: e.g., "desc"', ln=True)
    pdf.ln(5)

    # Supported Blockchains
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Supported Blockchains", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(
        0, 10, "The system supports multiple blockchains with priority order:", ln=True
    )
    pdf.cell(0, 10, "1. Ethereum", ln=True)
    pdf.cell(0, 10, "2. Polygon", ln=True)
    pdf.cell(0, 10, "3. BNB Smart Chain (BEP20)", ln=True)
    pdf.cell(0, 10, "4. Arbitrum", ln=True)
    pdf.cell(0, 10, "5. Optimistic", ln=True)
    pdf.cell(0, 10, "6. Avalanche C-Chain", ln=True)
    pdf.cell(0, 10, "7. Base", ln=True)
    pdf.cell(0, 10, "8. Solana", ln=True)
    pdf.ln(5)

    # Response Models
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Response Models", ln=True)
    pdf.ln(5)

    # Cryptocurrency Data Model
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cryptocurrency Data Model:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "class CryptocurrencySymbol_Mobula:", ln=True)
    pdf.cell(0, 10, "    id: int", ln=True)
    pdf.cell(0, 10, "    name: str", ln=True)
    pdf.cell(0, 10, "    symbol: str", ln=True)
    pdf.ln(5)

    # OHLCV Response Structure
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "OHLCV Response Structure:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "{", ln=True)
    pdf.cell(0, 10, '    "blockchain": str,', ln=True)
    pdf.cell(0, 10, '    "asset": str,', ln=True)
    pdf.cell(0, 10, '    "data": [', ln=True)
    pdf.cell(0, 10, "        {", ln=True)
    pdf.cell(0, 10, '            "timestamp": int,', ln=True)
    pdf.cell(0, 10, '            "open": float,', ln=True)
    pdf.cell(0, 10, '            "high": float,', ln=True)
    pdf.cell(0, 10, '            "low": float,', ln=True)
    pdf.cell(0, 10, '            "close": float,', ln=True)
    pdf.cell(0, 10, '            "volume": float', ln=True)
    pdf.cell(0, 10, "        }", ln=True)
    pdf.cell(0, 10, "    ]", ln=True)
    pdf.cell(0, 10, "}", ln=True)
    pdf.ln(5)

    # Error Handling
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Error Handling", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "The API client includes error handling for:", ln=True)
    pdf.cell(0, 10, "- HTTP errors", ln=True)
    pdf.cell(0, 10, "- Connection errors", ln=True)
    pdf.cell(0, 10, "- Invalid response formats", ln=True)
    pdf.cell(0, 10, "- Empty responses", ln=True)
    pdf.ln(5)

    # Rate Limiting
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Rate Limiting", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(
        0,
        10,
        "- The system includes built-in rate limiting and retry logic for API calls",
        ln=True,
    )
    pdf.cell(0, 10, "- Failed requests are logged for monitoring", ln=True)

    # Save the PDF
    pdf.output("mobula_api_documentation.pdf")


if __name__ == "__main__":
    create_mobula_docs_pdf()
