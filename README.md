# Svensk Aktiebevakning — första prototyp

En lokal Streamlit-app för att experimentera med svensk aktiebevakning, tekniska signaler, indikativ ATR-stop-loss, nyhetsrubriker och simulerade affärer. Den placerar inga riktiga order.

## Starta på Windows
1. Installera Python 3.11 eller nyare från https://www.python.org/downloads/ och välj att lägga Python i PATH.
2. Packa upp mappen.
3. Dubbelklicka `starta_windows.bat`.
4. När installationen är klar öppnas appen i webbläsaren. Om inte, gå till adressen som visas i terminalen (vanligen http://localhost:8501).

Alternativt kör i terminalen:
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Innehåll
- Förinställd lista med vanliga svenska aktier; aktier kan läggas till med Yahoo Finance-ticker.
- Dagliga historiska kurser via `yfinance`.
- SMA20/50/200, RSI, MACD, ATR, relativ volym, enkel signalpoäng och riskindikator.
- Indikativ stop-loss baserad på ATR.
- RSS-rubriker från Google News.
- Lokal SQLite-databas för bevakningslista och testaffärer.
- Förenklat historiskt test med explicita begränsningar.

## Viktiga begränsningar
- Yahoo Finance-data via `yfinance` är en tredjepartslösning för research/utbildning; datatäckning, aktualitet och villkor kan variera. Se yfinance-dokumentationen och Yahoo Finance-villkor.
- Signaler är regelbaserade heuristiker, inte maskininlärningsmodeller och inte verifierade prognoser.
- Nyhetsfunktionen visar rubriker och gör inte ännu en tillförlitlig sentimentanalys.
- Bevakning sker när appen körs/uppdateras. För varningar när appen är stängd behövs senare en separat schemalagd tjänst och notifieringskanal.
- SQLite-filen `aktieapp.db` sparar inställningar och testaffärer lokalt i projektmappen. Säkerhetskopiera filen om du vill behålla dina data.
- Stop-loss kan ge sämre avslut än beräknat vid kursgap eller låg likviditet.

Detta är en teknisk prototyp, inte investeringsrådgivning. Testa först med simulerade affärer och granska alla källor själv.
