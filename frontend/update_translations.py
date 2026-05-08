import re

file_path = "client/src/lib/translations.ts"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

en_add = """
    // Landing Page
    lp_hero_badge: "Satellite-Powered Farm Intelligence",
    lp_hero_title1: "Empowering the ",
    lp_hero_title2: "Future",
    lp_hero_title3: " of Farming",
    lp_hero_desc: "Leverage real-time satellite imagery and AI-driven insights to maximize yield, minimize waste, and cultivate a smarter future for your farm.",
    lp_btn_get_started: "Get Started Free",
    lp_btn_learn_more: "Learn More",
    lp_features_title: "All-in-One Farming Intelligence",
    lp_features_subtitle: "Our platform provides comprehensive tools to monitor and optimize every aspect of your farm.",
    lp_feat_sat_title: "Satellite Monitoring",
    lp_feat_sat_desc: "Monitor plant vitality with NDVI satellite imagery and detect stress before it spreads.",
    lp_feat_pest_title: "AI Pest Detection",
    lp_feat_pest_desc: "Upload a photo of affected crops and our CNN model identifies the disease and suggests treatments.",
    lp_feat_fin_title: "Financial Ledger",
    lp_feat_fin_desc: "Log income, expenses, and track your farm's PnL with our smart cost calculator.",
    lp_feat_yield_title: "Yield Prediction",
    lp_feat_yield_desc: "AI-driven forecasts that analyze historical data for better harvest planning.",
    lp_feat_market_title: "Market Prices & Weather",
    lp_feat_market_desc: "Get live mandi prices and real-time weather alerts to plan your interventions.",
    lp_feat_govt_title: "Government Schemes",
    lp_feat_govt_desc: "Discover and apply for relevant agricultural subsidies and insurance programs.",
    lp_feat_awd_title: "Carbon Credits (AWD)",
    lp_feat_awd_desc: "Adopt sustainable practices like AWD to earn extra income through carbon credits.",
    lp_how_title: "How to Use AgriSmart",
    lp_how_subtitle: "From setup to harvest, integrating our tools is as simple as 1-2-3-4.",
    lp_how_1_title: "Register & Map",
    lp_how_1_desc: "Create an account and draw your field boundaries on the map to start tracking.",
    lp_how_2_title: "Monitor & Log",
    lp_how_2_desc: "Regularly log your expenses and use satellite data to keep an eye on crop health.",
    lp_how_3_title: "Get AI Insights",
    lp_how_3_desc: "Receive pest warnings, weather alerts, and yield predictions automatically.",
    lp_how_4_title: "Sell Smartly",
    lp_how_4_desc: "Use live market prices to sell your harvest at the best mandi for maximum profit.",
    lp_ben_title: "Why Choose AgriSmart?",
    lp_ben_subtitle: "The direct benefits of bringing your farm online.",
    lp_ben_1_title: "Increase Yield by 20%",
    lp_ben_1_desc: "Data-driven decisions and early disease detection prevent major crop losses.",
    lp_ben_2_title: "Reduce Input Costs",
    lp_ben_2_desc: "Optimize fertilizer and water usage with precise satellite and weather tracking.",
    lp_ben_3_title: "Earn Extra Income",
    lp_ben_3_desc: "Access government schemes and sell carbon credits through sustainable farming.",
"""

hi_add = """
    // Landing Page
    lp_hero_badge: "सैटेलाइट आधारित कृषि बुद्धिमत्ता",
    lp_hero_title1: "खेती के ",
    lp_hero_title2: "भविष्य",
    lp_hero_title3: " को सशक्त बनाना",
    lp_hero_desc: "अपने खेत के लिए उपज को अधिकतम करने, बर्बादी को कम करने और एक स्मार्ट भविष्य बनाने के लिए रीयल-टाइम सैटेलाइट इमेजरी और एआई-संचालित अंतर्दृष्टि का लाभ उठाएं।",
    lp_btn_get_started: "मुफ़्त में शुरू करें",
    lp_btn_learn_more: "और जानें",
    lp_features_title: "ऑल-इन-वन फार्मिंग इंटेलिजेंस",
    lp_features_subtitle: "हमारा प्लेटफ़ॉर्म आपके खेत के हर पहलू की निगरानी और अनुकूलन करने के लिए व्यापक उपकरण प्रदान करता है।",
    lp_feat_sat_title: "सैटेलाइट निगरानी",
    lp_feat_sat_desc: "NDVI सैटेलाइट इमेजरी के साथ पौधों की जीवन शक्ति की निगरानी करें और तनाव फैलने से पहले उसका पता लगाएं।",
    lp_feat_pest_title: "एआई कीट पहचान",
    lp_feat_pest_desc: "प्रभावित फसलों की तस्वीर अपलोड करें और हमारा CNN मॉडल बीमारी की पहचान करता है और उपचार सुझाता है।",
    lp_feat_fin_title: "वित्तीय लेजर",
    lp_feat_fin_desc: "आय, व्यय लॉग करें, और हमारे स्मार्ट लागत कैलकुलेटर के साथ अपने खेत के लाभ-हानि को ट्रैक करें।",
    lp_feat_yield_title: "उपज पूर्वानुमान",
    lp_feat_yield_desc: "बेहतर फसल योजना के लिए ऐतिहासिक डेटा का विश्लेषण करने वाले एआई-संचालित पूर्वानुमान।",
    lp_feat_market_title: "बाजार मूल्य और मौसम",
    lp_feat_market_desc: "अपने हस्तक्षेपों की योजना बनाने के लिए लाइव मंडी मूल्य और रीयल-टाइम मौसम अलर्ट प्राप्त करें।",
    lp_feat_govt_title: "सरकारी योजनाएं",
    lp_feat_govt_desc: "प्रासंगिक कृषि सब्सिडी और बीमा कार्यक्रमों की खोज करें और आवेदन करें।",
    lp_feat_awd_title: "कार्बन क्रेडिट (AWD)",
    lp_feat_awd_desc: "कार्बन क्रेडिट के माध्यम से अतिरिक्त आय अर्जित करने के लिए AWD जैसी स्थायी प्रथाओं को अपनाएं।",
    lp_how_title: "AgriSmart का उपयोग कैसे करें",
    lp_how_subtitle: "सेटअप से लेकर कटाई तक, हमारे टूल को एकीकृत करना 1-2-3-4 जितना आसान है।",
    lp_how_1_title: "रजिस्टर करें और मैप करें",
    lp_how_1_desc: "एक खाता बनाएं और ट्रैकिंग शुरू करने के लिए मैप पर अपने खेत की सीमाएं खींचें।",
    lp_how_2_title: "निगरानी और लॉग",
    lp_how_2_desc: "नियमित रूप से अपने खर्चों को लॉग करें और फसल स्वास्थ्य पर नज़र रखने के लिए सैटेलाइट डेटा का उपयोग करें।",
    lp_how_3_title: "एआई अंतर्दृष्टि प्राप्त करें",
    lp_how_3_desc: "कीट चेतावनियां, मौसम अलर्ट और उपज पूर्वानुमान स्वचालित रूप से प्राप्त करें।",
    lp_how_4_title: "समझदारी से बेचें",
    lp_how_4_desc: "अधिकतम लाभ के लिए अपनी फसल को सबसे अच्छी मंडी में बेचने के लिए लाइव बाजार कीमतों का उपयोग करें।",
    lp_ben_title: "AgriSmart क्यों चुनें?",
    lp_ben_subtitle: "अपने खेत को ऑनलाइन लाने के प्रत्यक्ष लाभ।",
    lp_ben_1_title: "उपज में 20% की वृद्धि",
    lp_ben_1_desc: "डेटा-संचालित निर्णय और शीघ्र रोग का पता लगाने से फसल के बड़े नुकसान को रोका जा सकता है।",
    lp_ben_2_title: "इनपुट लागत कम करें",
    lp_ben_2_desc: "सटीक सैटेलाइट और मौसम ट्रैकिंग के साथ उर्वरक और पानी के उपयोग को अनुकूलित करें।",
    lp_ben_3_title: "अतिरिक्त आय अर्जित करें",
    lp_ben_3_desc: "सरकारी योजनाओं तक पहुंचें और स्थायी खेती के माध्यम से कार्बन क्रेडिट बेचें।",
"""

pa_add = """
    // Landing Page
    lp_hero_badge: "ਸੈਟੇਲਾਈਟ-ਅਧਾਰਤ ਖੇਤੀਬਾੜੀ ਇੰਟੈਲੀਜੈਂਸ",
    lp_hero_title1: "ਖੇਤੀ ਦੇ ",
    lp_hero_title2: "ਭਵਿੱਖ",
    lp_hero_title3: " ਨੂੰ ਸਸ਼ਕਤ ਬਣਾਉਣਾ",
    lp_hero_desc: "ਆਪਣੇ ਖੇਤ ਲਈ ਝਾੜ ਨੂੰ ਵੱਧ ਤੋਂ ਵੱਧ ਕਰਨ, ਬਰਬਾਦੀ ਨੂੰ ਘਟਾਉਣ ਅਤੇ ਇੱਕ ਸਮਾਰਟ ਭਵਿੱਖ ਬਣਾਉਣ ਲਈ ਰੀਅਲ-ਟਾਈਮ ਸੈਟੇਲਾਈਟ ਇਮੇਜਰੀ ਅਤੇ AI-ਸੰਚਾਲਿਤ ਸੂਝਾਂ ਦਾ ਲਾਭ ਉਠਾਓ।",
    lp_btn_get_started: "ਮੁਫਤ ਵਿੱਚ ਸ਼ੁਰੂ ਕਰੋ",
    lp_btn_learn_more: "ਹੋਰ ਜਾਣੋ",
    lp_features_title: "ਆਲ-ਇਨ-ਵਨ ਫਾਰਮਿੰਗ ਇੰਟੈਲੀਜੈਂਸ",
    lp_features_subtitle: "ਸਾਡਾ ਪਲੇਟਫਾਰਮ ਤੁਹਾਡੇ ਖੇਤ ਦੇ ਹਰ ਪਹਿਲੂ ਦੀ ਨਿਗਰਾਨੀ ਅਤੇ ਅਨੁਕੂਲਿਤ ਕਰਨ ਲਈ ਵਿਆਪਕ ਸਾਧਨ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ।",
    lp_feat_sat_title: "ਸੈਟੇਲਾਈਟ ਨਿਗਰਾਨੀ",
    lp_feat_sat_desc: "NDVI ਸੈਟੇਲਾਈਟ ਇਮੇਜਰੀ ਨਾਲ ਪੌਦਿਆਂ ਦੀ ਜੀਵਨਸ਼ਕਤੀ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ ਅਤੇ ਤਣਾਅ ਫੈਲਣ ਤੋਂ ਪਹਿਲਾਂ ਇਸਦਾ ਪਤਾ ਲਗਾਓ।",
    lp_feat_pest_title: "AI ਕੀੜਾ ਪਛਾਣ",
    lp_feat_pest_desc: "ਪ੍ਰਭਾਵਿਤ ਫਸਲਾਂ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ ਅਤੇ ਸਾਡਾ CNN ਮਾਡਲ ਬਿਮਾਰੀ ਦੀ ਪਛਾਣ ਕਰਦਾ ਹੈ ਅਤੇ ਇਲਾਜ ਦਾ ਸੁਝਾਅ ਦਿੰਦਾ ਹੈ।",
    lp_feat_fin_title: "ਵਿੱਤੀ ਲੇਜਰ",
    lp_feat_fin_desc: "ਆਮਦਨ, ਖਰਚੇ ਲੌਗ ਕਰੋ, ਅਤੇ ਸਾਡੇ ਸਮਾਰਟ ਲਾਗਤ ਕੈਲਕੁਲੇਟਰ ਨਾਲ ਆਪਣੇ ਖੇਤ ਦੇ ਮੁਨਾਫੇ-ਨੁਕਸਾਨ ਨੂੰ ਟਰੈਕ ਕਰੋ।",
    lp_feat_yield_title: "ਝਾੜ ਪੂਰਵ-ਅਨੁਮਾਨ",
    lp_feat_yield_desc: "ਬਿਹਤਰ ਫਸਲ ਯੋਜਨਾਬੰਦੀ ਲਈ ਇਤਿਹਾਸਕ ਡੇਟਾ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰਨ ਵਾਲੇ AI-ਸੰਚਾਲਿਤ ਪੂਰਵ-ਅਨੁਮਾਨ।",
    lp_feat_market_title: "ਬਾਜ਼ਾਰ ਦੀਆਂ ਕੀਮਤਾਂ ਅਤੇ ਮੌਸਮ",
    lp_feat_market_desc: "ਆਪਣੇ ਦਖਲ ਦੀ ਯੋਜਨਾ ਬਣਾਉਣ ਲਈ ਲਾਈਵ ਮੰਡੀ ਦੀਆਂ ਕੀਮਤਾਂ ਅਤੇ ਰੀਅਲ-ਟਾਈਮ ਮੌਸਮ ਅਲਰਟ ਪ੍ਰਾਪਤ ਕਰੋ।",
    lp_feat_govt_title: "ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ",
    lp_feat_govt_desc: "ਢੁਕਵੀਆਂ ਖੇਤੀਬਾੜੀ ਸਬਸਿਡੀਆਂ ਅਤੇ ਬੀਮਾ ਪ੍ਰੋਗਰਾਮਾਂ ਦੀ ਖੋਜ ਕਰੋ ਅਤੇ ਅਪਲਾਈ ਕਰੋ।",
    lp_feat_awd_title: "ਕਾਰਬਨ ਕ੍ਰੈਡਿਟ (AWD)",
    lp_feat_awd_desc: "ਕਾਰਬਨ ਕ੍ਰੈਡਿਟ ਦੁਆਰਾ ਵਾਧੂ ਆਮਦਨ ਕਮਾਉਣ ਲਈ AWD ਵਰਗੇ ਟਿਕਾਊ ਅਭਿਆਸਾਂ ਨੂੰ ਅਪਣਾਓ।",
    lp_how_title: "AgriSmart ਦੀ ਵਰਤੋਂ ਕਿਵੇਂ ਕਰੀਏ",
    lp_how_subtitle: "ਸੈੱਟਅੱਪ ਤੋਂ ਲੈ ਕੇ ਵਾਢੀ ਤੱਕ, ਸਾਡੇ ਟੂਲਸ ਨੂੰ ਏਕੀਕ੍ਰਿਤ ਕਰਨਾ 1-2-3-4 ਜਿੰਨਾ ਸੌਖਾ ਹੈ।",
    lp_how_1_title: "ਰਜਿਸਟਰ ਕਰੋ ਅਤੇ ਮੈਪ ਕਰੋ",
    lp_how_1_desc: "ਇੱਕ ਖਾਤਾ ਬਣਾਓ ਅਤੇ ਟਰੈਕਿੰਗ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਨਕਸ਼ੇ 'ਤੇ ਆਪਣੇ ਖੇਤ ਦੀਆਂ ਸੀਮਾਵਾਂ ਖਿੱਚੋ।",
    lp_how_2_title: "ਨਿਗਰਾਨੀ ਅਤੇ ਲੌਗ",
    lp_how_2_desc: "ਨਿਯਮਿਤ ਤੌਰ 'ਤੇ ਆਪਣੇ ਖਰਚਿਆਂ ਨੂੰ ਲੌਗ ਕਰੋ ਅਤੇ ਫਸਲ ਦੀ ਸਿਹਤ 'ਤੇ ਨਜ਼ਰ ਰੱਖਣ ਲਈ ਸੈਟੇਲਾਈਟ ਡੇਟਾ ਦੀ ਵਰਤੋਂ ਕਰੋ।",
    lp_how_3_title: "AI ਸੂਝ ਪ੍ਰਾਪਤ ਕਰੋ",
    lp_how_3_desc: "ਕੀੜਿਆਂ ਦੀਆਂ ਚੇਤਾਵਨੀਆਂ, ਮੌਸਮ ਸੰਬੰਧੀ ਚੇਤਾਵਨੀਆਂ, ਅਤੇ ਝਾੜ ਦੀਆਂ ਭਵਿੱਖਬਾਣੀਆਂ ਆਪਣੇ ਆਪ ਪ੍ਰਾਪਤ ਕਰੋ।",
    lp_how_4_title: "ਸਮਝਦਾਰੀ ਨਾਲ ਵੇਚੋ",
    lp_how_4_desc: "ਵੱਧ ਤੋਂ ਵੱਧ ਮੁਨਾਫੇ ਲਈ ਆਪਣੀ ਫਸਲ ਨੂੰ ਸਭ ਤੋਂ ਵਧੀਆ ਮੰਡੀ ਵਿੱਚ ਵੇਚਣ ਲਈ ਲਾਈਵ ਮਾਰਕੀਟ ਕੀਮਤਾਂ ਦੀ ਵਰਤੋਂ ਕਰੋ।",
    lp_ben_title: "AgriSmart ਕਿਉਂ ਚੁਣੀਏ?",
    lp_ben_subtitle: "ਆਪਣੇ ਖੇਤ ਨੂੰ ਆਨਲਾਈਨ ਲਿਆਉਣ ਦੇ ਸਿੱਧੇ ਲਾਭ।",
    lp_ben_1_title: "ਝਾੜ ਵਿੱਚ 20% ਦਾ ਵਾਧਾ",
    lp_ben_1_desc: "ਡੇਟਾ-ਸੰਚਾਲਿਤ ਫੈਸਲੇ ਅਤੇ ਜਲਦੀ ਬਿਮਾਰੀ ਦਾ ਪਤਾ ਲਗਾਉਣਾ ਫਸਲ ਦੇ ਵੱਡੇ ਨੁਕਸਾਨ ਨੂੰ ਰੋਕਦਾ ਹੈ।",
    lp_ben_2_title: "ਇਨਪੁਟ ਲਾਗਤਾਂ ਨੂੰ ਘਟਾਓ",
    lp_ben_2_desc: "ਸਹੀ ਸੈਟੇਲਾਈਟ ਅਤੇ ਮੌਸਮ ਟਰੈਕਿੰਗ ਨਾਲ ਖਾਦ ਅਤੇ ਪਾਣੀ ਦੀ ਵਰਤੋਂ ਨੂੰ ਅਨੁਕੂਲਿਤ ਕਰੋ।",
    lp_ben_3_title: "ਵਾਧੂ ਆਮਦਨ ਕਮਾਓ",
    lp_ben_3_desc: "ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ ਤੱਕ ਪਹੁੰਚ ਕਰੋ ਅਤੇ ਟਿਕਾਊ ਖੇਤੀ ਰਾਹੀਂ ਕਾਰਬਨ ਕ੍ਰੈਡਿਟ ਵੇਚੋ।",
"""

ml_add = """
    // Landing Page
    lp_hero_badge: "സാറ്റലൈറ്റ് അധിഷ്ഠിത കാർഷിക ബുദ്ധി",
    lp_hero_title1: "കൃഷിയുടെ ",
    lp_hero_title2: "ഭാവി",
    lp_hero_title3: " ശാക്തീകരിക്കുന്നു",
    lp_hero_desc: "വിളവ് വർദ്ധിപ്പിക്കാനും പാഴാകുന്നത് കുറയ്ക്കാനും നിങ്ങളുടെ കൃഷിയിടത്തിന് മികച്ച ഭാവി സൃഷ്ടിക്കാനും തത്സമയ സാറ്റലൈറ്റ് ചിത്രങ്ങളും AI അധിഷ്ഠിത ഉൾക്കാഴ്ചകളും പ്രയോജനപ്പെടുത്തുക.",
    lp_btn_get_started: "സൗജന്യമായി ആരംഭിക്കുക",
    lp_btn_learn_more: "കൂടുതൽ അറിയുക",
    lp_features_title: "ഓൾ-ഇൻ-വൺ ഫാമിംഗ് ഇന്റലിജൻസ്",
    lp_features_subtitle: "നിങ്ങളുടെ കൃഷിയിടത്തിന്റെ ഓരോ വശവും നിരീക്ഷിക്കാനും മെച്ചപ്പെടുത്താനും ഞങ്ങളുടെ പ്ലാറ്റ്ഫോം സമഗ്രമായ ഉപകരണങ്ങൾ നൽകുന്നു.",
    lp_feat_sat_title: "സാറ്റലൈറ്റ് നിരീക്ഷണം",
    lp_feat_sat_desc: "NDVI സാറ്റലൈറ്റ് ഇമേജറി ഉപയോഗിച്ച് സസ്യങ്ങളുടെ ജീവശക്തി നിരീക്ഷിക്കുകയും സമ്മർദ്ദം പടരുന്നതിന് മുമ്പ് കണ്ടെത്തുകയും ചെയ്യുക.",
    lp_feat_pest_title: "AI കീട നിയന്ത്രണം",
    lp_feat_pest_desc: "ബാധിച്ച വിളകളുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക, ഞങ്ങളുടെ CNN മോഡൽ രോഗം തിരിച്ചറിയുകയും ചികിത്സകൾ നിർദ്ദേശിക്കുകയും ചെയ്യുന്നു.",
    lp_feat_fin_title: "സാമ്പത്തിക ലെഡ്ജർ",
    lp_feat_fin_desc: "വരുമാനം, ചെലവുകൾ എന്നിവ രേഖപ്പെടുത്തുക, ഞങ്ങളുടെ സ്മാർട്ട് കോസ്റ്റ് കാൽക്കുലേറ്റർ ഉപയോഗിച്ച് നിങ്ങളുടെ ഫീൽഡിന്റെ PnL ട്രാക്ക് ചെയ്യുക.",
    lp_feat_yield_title: "വിളവ് പ്രവചനം",
    lp_feat_yield_desc: "മികച്ച വിളവെടുപ്പ് ആസൂത്രണത്തിനായി ചരിത്രപരമായ ഡാറ്റ വിശകലനം ചെയ്യുന്ന AI-അധിഷ്ഠിത പ്രവചനങ്ങൾ.",
    lp_feat_market_title: "വിപണി വിലയും കാലാവസ്ഥയും",
    lp_feat_market_desc: "നിങ്ങളുടെ ഇടപെടലുകൾ ആസൂത്രണം ചെയ്യുന്നതിനായി തത്സമയ മണ്ഡി വിലകളും കാലാവസ്ഥാ അലേർട്ടുകളും നേടുക.",
    lp_feat_govt_title: "സർക്കാർ പദ്ധതികൾ",
    lp_feat_govt_desc: "പ്രസക്തമായ കാർഷിക സബ്‌സിഡികളും ഇൻഷുറൻസ് പ്രോഗ്രാമുകളും കണ്ടെത്തുകയും അപേക്ഷിക്കുകയും ചെയ്യുക.",
    lp_feat_awd_title: "കാർബൺ ക്രെഡിറ്റുകൾ (AWD)",
    lp_feat_awd_desc: "കാർബൺ ക്രെഡിറ്റുകളിലൂടെ അധിക വരുമാനം നേടുന്നതിന് AWD പോലുള്ള സുസ്ഥിര രീതികൾ സ്വീകരിക്കുക.",
    lp_how_title: "AgriSmart എങ്ങനെ ഉപയോഗിക്കാം",
    lp_how_subtitle: "സജ്ജീകരണം മുതൽ വിളവെടുപ്പ് വരെ, ഞങ്ങളുടെ ഉപകരണങ്ങൾ സംയോജിപ്പിക്കുന്നത് 1-2-3-4 പോലെ ലളിതമാണ്.",
    lp_how_1_title: "രജിസ്റ്റർ ചെയ്യുക, മാപ്പ് ചെയ്യുക",
    lp_how_1_desc: "ഒരു അക്കൗണ്ട് സൃഷ്ടിച്ച് ട്രാക്കിംഗ് ആരംഭിക്കുന്നതിന് മാപ്പിൽ നിങ്ങളുടെ ഫീൽഡ് അതിരുകൾ വരയ്ക്കുക.",
    lp_how_2_title: "നിരീക്ഷിക്കുക, ലോഗ് ചെയ്യുക",
    lp_how_2_desc: "നിങ്ങളുടെ ചെലവുകൾ കൃത്യമായി രേഖപ്പെടുത്തുകയും വിളകളുടെ ആരോഗ്യം നിരീക്ഷിക്കാൻ സാറ്റലൈറ്റ് ഡാറ്റ ഉപയോഗിക്കുകയും ചെയ്യുക.",
    lp_how_3_title: "AI ഉൾക്കാഴ്ചകൾ നേടുക",
    lp_how_3_desc: "കീട മുന്നറിയിപ്പുകൾ, കാലാവസ്ഥാ അലേർട്ടുകൾ, വിള പ്രവചനങ്ങൾ എന്നിവ യാന്ത്രികമായി സ്വീകരിക്കുക.",
    lp_how_4_title: "ബുദ്ധിപൂർവ്വം വിൽക്കുക",
    lp_how_4_desc: "പരമാവധി ലാഭത്തിനായി മികച്ച മണ്ഡിയിൽ നിങ്ങളുടെ വിള വിൽക്കാൻ തത്സമയ വിപണി വിലകൾ ഉപയോഗിക്കുക.",
    lp_ben_title: "എന്തുകൊണ്ട് AgriSmart തിരഞ്ഞെടുക്കണം?",
    lp_ben_subtitle: "നിങ്ങളുടെ കൃഷിയിടം ഓൺലൈനിൽ കൊണ്ടുവരുന്നതിന്റെ നേരിട്ടുള്ള നേട്ടങ്ങൾ.",
    lp_ben_1_title: "വിളവിൽ 20% വർദ്ധനവ്",
    lp_ben_1_desc: "ഡാറ്റ അധിഷ്ഠിത തീരുമാനങ്ങളും നേരത്തെയുള്ള രോഗനിർണ്ണയവും വലിയ വിളനാശം തടയുന്നു.",
    lp_ben_2_title: "ഇൻപുട്ട് ചെലവുകൾ കുറയ്ക്കുക",
    lp_ben_2_desc: "കൃത്യമായ സാറ്റലൈറ്റ്, കാലാവസ്ഥാ ട്രാക്കിംഗ് ഉപയോഗിച്ച് വളം, ജല ഉപയോഗം എന്നിവ ഒപ്റ്റിമൈസ് ചെയ്യുക.",
    lp_ben_3_title: "അധിക വരുമാനം നേടുക",
    lp_ben_3_desc: "സർക്കാർ പദ്ധതികൾ പ്രയോജനപ്പെടുത്തുകയും സുസ്ഥിര കൃഷിയിലൂടെ കാർബൺ ക്രെഡിറ്റുകൾ വിൽക്കുകയും ചെയ്യുക.",
"""

def insert_before(content, lang_key, text_to_insert):
    pattern = rf"(  {lang_key}: {{.*?)(  }},)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"Could not find {lang_key} block")
        return content
    
    return content[:match.start(2)] + text_to_insert + content[match.start(2):]

content = insert_before(content, "en", en_add)
content = insert_before(content, "hi", hi_add)
content = insert_before(content, "pa", pa_add)
content = insert_before(content, "ml", ml_add)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Translations updated successfully.")
