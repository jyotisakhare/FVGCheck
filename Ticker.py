from datetime import datetime, timedelta

# Get the current date and time
current_datetime = datetime.now()


startDaily = (current_datetime - timedelta(days=5)).strftime('%Y-%m-%d')
endDaily = current_datetime.strftime('%Y-%m-%d')

startHr = (current_datetime - timedelta(days=2)).strftime('%Y-%m-%d')
endHr = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

stockPriceThreashHold = 15000

startW = (current_datetime - timedelta(days=35)).strftime('%Y-%m-%d')
endW = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

startM = (current_datetime - timedelta(days=180)).strftime('%Y-%m-%d')
endM = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

isGoodFVG = True
tickerGroup = "NIFTY250"

def get_tickers(type):
    if type == "NIFTY250":
        return ['3MINDIA.NS', 'ABB.NS', 'ABBOTINDIA.NS', 'ABCAPITAL.NS', 'ABFRL.NS', 'ACC.NS', 'ADANIENSOL.NS', 'ADANIENT.NS',
                'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'AIAENG.NS', 'AJANTPHARM.NS', 'ALKEM.NS', 'AMBUJACEM.NS',
                'APLAPOLLO.NS', 'APOLLOHOSP.NS', 'APOLLOTYRE.NS', 'ASHOKLEY.NS', 'ASIANPAINT.NS', 'ASTRAL.NS', 'ATGL.NS', 'ATUL.NS',
                'AUBANK.NS', 'AUROPHARMA.NS', 'AWL.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BAJAJHLDNG.NS', 'BAJFINANCE.NS',
                'BALKRISIND.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BANKINDIA.NS', 'BATAINDIA.NS', 'BAYERCROP.NS', 'BDL.NS', 'BEL.NS',
                'BERGEPAINT.NS', 'BHARATFORG.NS', 'BHARTIARTL.NS', 'BHEL.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'BPCL.NS', 'BRITANNIA.NS',
                'BSE.NS', 'CANBK.NS', 'CARBORUNIV.NS', 'CGPOWER.NS', 'CHOLAFIN.NS', 'CIPLA.NS', 'COALINDIA.NS', 'COFORGE.NS', 'COLPAL.NS',
                'CONCOR.NS', 'COROMANDEL.NS', 'CRISIL.NS', 'CUMMINSIND.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 'DELHIVERY.NS',
                'DEVYANI.NS', 'DIVISLAB.NS', 'DIXON.NS', 'DLF.NS', 'DMART.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'EMAMILTD.NS', 'ENDURANCE.NS',
                'ESCORTS.NS', 'FACT.NS', 'FEDERALBNK.NS', 'FLUOROCHEM.NS', 'FORTIS.NS', 'GAIL.NS', 'GICRE.NS', 'GLAND.NS', 'GLAXO.NS', 'GMRINFRA.NS',
                'GODREJCP.NS', 'GODREJIND.NS', 'GODREJPROP.NS', 'GRASIM.NS', 'GRINDWELL.NS', 'GUJGASLTD.NS', 'HAL.NS', 'HAVELLS.NS', 'HCLTECH.NS',
                'HDFCAMC.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDPETRO.NS', 'HINDUNILVR.NS', 'HINDZINC.NS', 'HONAUT.NS',
                'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'IDBI.NS', 'IDEA.NS', 'IDFCFIRSTB.NS', 'IGL.NS', 'INDHOTEL.NS', 'INDIANB.NS', 'INDIGO.NS',
                'INDUSINDBK.NS', 'INDUSTOWER.NS', 'INFY.NS', 'IOC.NS', 'IPCALAB.NS', 'IRCTC.NS', 'IRFC.NS', 'ISEC.NS', 'ITC.NS', 'JINDALSTEL.NS', 'JIOFIN.NS',
                'JKCEMENT.NS', 'JSL.NS', 'JSWENERGY.NS', 'JSWINFRA.NS', 'JSWSTEEL.NS', 'JUBLFOOD.NS', 'KAJARIACER.NS', 'KALYANKJIL.NS', 'KANSAINER.NS',
                'KEI.NS', 'KOTAKBANK.NS', 'KPITTECH.NS', 'KPRMILL.NS', 'LALPATHLAB.NS', 'LAURUSLABS.NS', 'LICHSGFIN.NS', 'LICI.NS', 'LINDEINDIA.NS', 'LLOYDSME.NS',
                'LODHA.NS', 'LT.NS', 'LTF.NS', 'LTIM.NS', 'LTTS.NS', 'LUPIN.NS', 'M&M.NS', 'M&MFIN.NS', 'MAHABANK.NS', 'MANKIND.NS', 'MANYAVAR.NS', 'MARICO.NS', 'MARUTI.NS', 'MAXHEALTH.NS', 'MAZDOCK.NS', 'METROBRAND.NS', 'MFSL.NS', 'MOTHERSON.NS', 'MPHASIS.NS', 'MRF.NS', 'MSUMI.NS',
                'MUTHOOTFIN.NS', 'NAUKRI.NS', 'NESTLEIND.NS', 'NHPC.NS', 'NIACL.NS', 'NMDC.NS', 'NTPC.NS', 'NYKAA.NS', 'OBEROIRLTY.NS', 'OFSS.NS', 'OIL.NS', 'ONGC.NS', 'PAGEIND.NS', 'PATANJALI.NS', 'PAYTM.NS', 'PEL.NS', 'PERSISTENT.NS', 'PETRONET.NS', 'PFC.NS', 'PGHH.NS', 'PHOENIXLTD.NS', 'PIDILITIND.NS', 'PIIND.NS', 'PNB.NS', 'POLICYBZR.NS', 'POLYCAB.NS', 'POONAWALLA.NS', 'POWERGRID.NS', 'PRESTIGE.NS', 'RAMCOCEM.NS', 'RECLTD.NS',
                'RELIANCE.NS', 'RVNL.NS', 'SAIL.NS', 'SBICARD.NS', 'SBILIFE.NS', 'SBIN.NS', 'SCHAEFFLER.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SJVN.NS', 'SKFINDIA.NS', 'SOLARINDS.NS', 'SONACOMS.NS', 'SRF.NS', 'STARHEALTH.NS', 'SUMICHEM.NS', 'SUNDARMFIN.NS', 'SUNDRMFAST.NS', 'SUNPHARMA.NS', 'SUNTV.NS', 'SUPREMEIND.NS', 'SUZLON.NS', 'SYNGENE.NS', 'TATACHEM.NS', 'TATACOMM.NS', 'TATACONSUM.NS', 'TATAELXSI.NS',
                'TATAMOTORS.NS', 'TATAMTRDVR.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TATATECH.NS', 'TCS.NS', 'TECHM.NS', 'THERMAX.NS', 'TIINDIA.NS', 'TIMKEN.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TORNTPOWER.NS', 'TRENT.NS', 'TVSMOTOR.NS', 'UBL.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS', 'UNITDSPR.NS', 'UNOMINDA.NS', 'UPL.NS', 'VBL.NS', 'VEDL.NS', 'VOLTAS.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZEEL.NS', 'ZFCVINDIA.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS']
    elif type == "UNDER500":
        return ["EIEL.NS", "HINDZINC.NS", "LEMONTREE.NS", "SAMHI.NS", "DELHIVERY.NS", "SAPPHIRE.NS", "PNCINFRA.NS",
                "CHEMPLASTS.NS", "CHALET.NS", "MASFIN.NS", "KRBL.NS", "ONGC.NS", "IDFCFIRSTB.NS", "BANKBARODA.NS",
                "GSFC.NS", "ITC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "BEL.NS", "JIOFIN.NS", "IRFC.NS",
                "ASHOKLEY.NS", "GENUSPOWER.NS", "TEXRAIL.NS", "PARACABLES.NS", "KRISHIVAL.NS", "BCLIND.NS", "IEX.NS",
                "VEDL.NS", "INDUSTOWER.NS", "MANGCHEFER.NS", "CUB.NS", "BANDHANBNK.NS", "CSBBANK.NS", "LTFOODS.NS",
                "MOTHERSON.NS", "NBCC.NS"]
    elif type == "MINE":
        return ["ABSLAMC.NS", "ADANIENSOL.NS", "AFFLE.NS", "ALKEM.NS", "ARE&M.NS", "ANANTRAJ.NS", "APARINDS.NS",
                "APOLLOHOSP.NS", "APOLLOTYRE.NS", "ASIANPAINT.NS", "AVANTIFEED.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
                "BAJAJFINSV.NS", "BAJAJHFL.NS", "BAJFINANCE.NS", "BECTORFOOD.NS", "BHARTIARTL.NS", "BLUESTARCO.NS",
                "BRIGADE.NS", "BRITANNIA.NS", "BSOFT.NS", "CANFINHOME.NS", "CASTROLIND.NS", "CDSL.NS", "CEATLTD.NS",
                "CESC.NS", "CHAMBLFERT.NS", "CMSINFO.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "COROMANDEL.NS",
                "CRAFTSMAN.NS", "CROMPTON.NS", "CYIENT.NS", "DATAPATTNS.NS", "DBEIL.NS", "DIVISLAB.NS", "DLF.NS",
                "DMART.NS", "DRREDDY.NS", "EICHERMOT.NS", "EMAMILTD.NS", "EMBASSY.BS", "ENDURANCE.NS", "EQUITASBNK.NS",
                "EXIDEIND.NS", "FSL.NS", "GABRIEL.NS", "GAIL.NS", "GESHIP.NS", "GHCL.NS", "GLS.NS", "GODREJPROP.NS",
                "GOLDBEES.NS", "GRASIM.NS", "HAL.NS", "HAPPSTMNDS.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
                "HEROMOTOCO.NS", "HGINFRA.NS", "HINDUNILVR.NS", "HSCL.NS", "ICICIBANK.NS", "IDFCFIRSTB.NS", "IEX.NS",
                "IKS.NS", "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INDUSTOWER.NS", "INFY.NS", "IRFC.NS", "ITC.NS",
                "JINDALSAW.NS", "JIOFIN.NS", "JKIL.NS", "JKLAKSHMI.NS", "JKTYRE.NS", "JSL.NS", "JUNIORBEES.NS",
                "KARURVYSYA.NS", "KFINTECH.NS", "KIRLOSBROS.NS", "KIRLOSENG.NS", "KNRCON.NS", "KOTAKBANK.NS",
                "KPITTECH.NS", "LTF.NS", "LIQUIDBEES.NS", "LIQUIDCASE.NS", "LTFOODS.NS", "LTIM.NS", "LUPIN.NS",
                "M&M.NS", "MAHSEAMLES.NS", "MANINFRA.NS", "MANYAVAR.NS", "MAPMYINDIA.NS", "MARICO.NS", "MARKSANS.NS",
                "MAZDOCK.NS", "MID150BEES.NS", "MID150CASE.NS", "MINDACORP.NS", "MINDSPACE.NS", "MON100.NS",
                "MOTHERSON.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MRPL.NS", "MSUMI.NS", "MTARTECH.NS", "MUTHOOTFIN.NS",
                "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NCC.NS", "NESTLEIND.NS", "NEWGEN.NS", "NH.NS",
                "NHPC.NS", "NIFTYBEES.NS", "NMDC.NS", "NTPC.NS", "NXST.NS", "OBEROIRLTY.NS", "OFSS.NS", "OLECTRA.NS",
                "ONGC.NS", "PCBL.NS", "PERSISTENT.NS", "PFC.NS", "PHOENIXLTD.NS", "PIDILITIND.NS", "PNBHOUSING.NS",
                "PNCINFRA.NS", "PNGJL.NS", "POWERGRID.NS", "PRESTIGE.NS", "RAYMOND.NS", "REDINGTON.NS", "RELIANCE.NS",
                "RVNL.NS", "SBIN.NS", "SETFNIF50.NS", "SOBHA.NS", "SONACOMS.NS", "SUNDRMFAST.NS", "SUNPHARMA.NS",
                "SUNTV.NS", "SUZLON.NS", "TATACOMM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS",
                "TCS.NS", "TIMETECHNO.NS", "TIPSMUSIC.NS", "TITAN.NS", "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS",
                "UTIAMC.NS", "VBL.NS", "VEDL.NS", "VGUARD.NS", "VRLLOG.NS", "VSTIND.NS", "WELCORP.NS", "WIPRO.NS",
                "WONDERLA.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"]
    elif type == "FAV":
        return [ "AFFLE.NS",  "ASIANPAINT.NS", "AXISBANK.NS",
                "BAJAJFINSV.NS", "BAJAJHFL.NS", "BAJFINANCE.NS",  "BHARTIARTL.NS", "BLUESTARCO.NS",
               "BSOFT.NS", "CDSL.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "DATAPATTNS.NS","DLF.NS",
                "DMART.NS", "DRREDDY.NS", "EICHERMOT.NS", "EQUITASBNK.NS",
                "EXIDEIND.NS", "HAL.NS", "HAPPSTMNDS.NS","HDFCBANK.NS",
                 "HINDUNILVR.NS",  "ICICIBANK.NS", "IDFCFIRSTB.NS", "IEX.NS",
                 "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INFY.NS", "IRFC.NS", "ITC.NS",
               "JIOFIN.NS",  "KOTAKBANK.NS",
                "KPITTECH.NS", "LTF.NS",
                "M&M.NS", "MAHSEAMLES.NS", "MAPMYINDIA.NS", "MARICO.NS",
                "MAZDOCK.NS",  "MINDACORP.NS", "MON100.NS",
                "MOTHERSON.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MRPL.NS", "MSUMI.NS", "MTARTECH.NS", "MUTHOOTFIN.NS",
               "NAVINFLUOR.NS", "NEWGEN.NS",
               "OLECTRA.NS",
                "ONGC.NS", "PCBL.NS","PFC.NS", "PNBHOUSING.NS",
                "PNCINFRA.NS", "PNGJL.NS", "POWERGRID.NS", "REDINGTON.NS", "RELIANCE.NS",
                "RVNL.NS", "SBIN.NS", "SETFNIF50.NS",
                "SUZLON.NS", "TATACOMM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS",
                "TCS.NS", "TIMETECHNO.NS",  "TITAN.NS", "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS",
                "VBL.NS", "VEDL.NS", "VRLLOG.NS", "WIPRO.NS",
                "WONDERLA.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
                 # "policy bazar",
                 # "Delhivery",
                 # APL Apollo Tubes,
                 # Max Financial Services:
                 ]
    elif type == "SINGLE":
        return ["INDHOTEL.NS"]
    elif type == "US":
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META",
    "TSLA", "NFLX", "ADBE", "AMD", "INTC", "AVGO", "QCOM",
    "MU", "COST", "PEP", "PYPL", "PLTR", "SNOW", # Exchanges
    "COIN", "HOOD", "BKKT",

    # Miners
    "MARA", "RIOT", "CLSK", "HUT", "BITF", "WULF",

    # Payments / FinTech
    "PYPL", "SQ", "V", "MA",

    # Tech / Holdings
    "TSLA", "MSTR", "NVDA", "IBM",

    # Financials
    "GS", "JPM", "BLK"]
    elif type == "RAVI":
        return ["TRANSRAILL.NS", "SHAKTIPUMP.NS", "MOTILALOFS.NS", "E2E.NS", "EPACK.NS", "PNGJL.NS", "PCBL.NS",
                "WAAREEENER.NS", "SAHASRA.NS", "TEJASNET.NS", "ORIENTTECH.NS", "KAYNES.NS", "IGIL.NS", "VMM.NS",
                "SAILIFE.NS", "EMSLIMITED.NS", "WABAG.NS", "RAJESH.BS", "EIEL.NS", "PIGL.NS", "THOMASCOTT.NS",
                "TEMBO.NS", "SALZERELEC.NS", "PREMIERENE.NS", "PGEL.NS", "IZMO.NS", "PPLPHARMA.NS", "BSE.NS", "CDSL.NS",
                "ANGELONE.NS", "DIXON.NS", "MCX.NS", "VPRPL.NS", "KRN.NS"]
    elif type == "ALL":
        ticker = get_tickers("MINE") + get_tickers("UNDER500") + get_tickers("NIFTY100") + get_tickers("RAVI")
        return ticker
    return []

print(get_tickers("SINGLE"))



print(f"Current date and time: {startDaily}")
print(f"Yesterday's date and time: {startM}")



