import re

file_path = "client/src/lib/translations.ts"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

en_detailed = """    lp_how_title: "How to Use AgriSmart",
    lp_how_subtitle: "A comprehensive journey from initial setup to a profitable harvest.",
    lp_how_1_title: "Register & Map Your Field",
    lp_how_1_desc: "Create your free account in less than a minute. Using our integrated map interface, simply draw the boundaries of your field. This initializes our satellite connection, instantly fetching historical and real-time vegetative indices like NDVI for your specific plot.",
    lp_how_2_title: "Monitor Health & Log Expenses",
    lp_how_2_desc: "Move away from paper notebooks. Use our digital financial ledger to record every seed, fertilizer, and labor expense. Simultaneously, keep a daily eye on crop health using our automated satellite scans that highlight moisture stress or growth issues before they become visible to the naked eye.",
    lp_how_3_title: "Leverage AI Insights & Alerts",
    lp_how_3_desc: "Our platform works 24/7. Snap a photo of a sickly plant and our advanced AI vision model will identify the disease and recommend treatments. You'll also receive proactive alerts for severe weather or sudden pest outbreaks in your district.",
    lp_how_4_title: "Predict Yield & Sell Smartly",
    lp_how_4_desc: "Don't guess the market. Access real-time mandi prices across your state. Our advanced prediction models estimate your total harvest volume, helping you negotiate better contracts and sell at the optimal time for maximum profit.",
    lp_ben_title: "Why Choose AgriSmart?",
    lp_ben_subtitle: "Transform your traditional farming methods into a highly optimized, data-driven agribusiness.",
    lp_ben_1_title: "Increase Yield by up to 20%",
    lp_ben_1_desc: "Stop guessing and start knowing. Data-driven farming ensures your crops get exactly what they need, when they need it. Early disease detection prevents minor infections from destroying your entire harvest, securing your hard work and increasing overall output.",
    lp_ben_2_title: "Drastically Reduce Input Costs",
    lp_ben_2_desc: "Over-fertilizing and over-watering don't just harm the soil, they drain your wallet. Our precise satellite tracking and weather integration tell you exactly when to spray and when to save, cutting unnecessary chemical and water expenses significantly.",
    lp_ben_3_title: "Unlock Extra Income Streams",
    lp_ben_3_desc: "Farming goes beyond the harvest. Discover and apply for relevant government subsidies. Plus, by adopting sustainable practices like AWD (Alternate Wetting and Drying), you can verify your water savings and sell Carbon Credits directly through our platform."""

hi_detailed = """    lp_how_title: "AgriSmart का उपयोग कैसे करें",
    lp_how_subtitle: "प्रारंभिक सेटअप से लेकर लाभदायक फसल तक की एक व्यापक यात्रा।",
    lp_how_1_title: "रजिस्टर करें और अपना खेत मैप करें",
    lp_how_1_desc: "एक मिनट से भी कम समय में अपना निःशुल्क खाता बनाएं। हमारे एकीकृत मानचित्र इंटरफ़ेस का उपयोग करके, बस अपने खेत की सीमाएं खींचें। यह हमारे सैटेलाइट कनेक्शन को प्रारंभ करता है, जो तुरंत आपके विशिष्ट भूखंड के लिए ऐतिहासिक और वास्तविक समय के वानस्पतिक सूचकांक (जैसे NDVI) प्राप्त करता है।",
    lp_how_2_title: "स्वास्थ्य की निगरानी करें और खर्च दर्ज करें",
    lp_how_2_desc: "कागज की नोटबुक से आगे बढ़ें। हर बीज, उर्वरक और श्रम व्यय को रिकॉर्ड करने के लिए हमारे डिजिटल वित्तीय लेजर का उपयोग करें। साथ ही, हमारे स्वचालित सैटेलाइट स्कैन का उपयोग करके फसल के स्वास्थ्य पर दैनिक नज़र रखें जो नमी के तनाव या विकास के मुद्दों को नग्न आंखों से दिखाई देने से पहले ही उजागर कर देते हैं।",
    lp_how_3_title: "एआई अंतर्दृष्टि और अलर्ट का लाभ उठाएं",
    lp_how_3_desc: "हमारा प्लेटफॉर्म 24/7 काम करता है। एक बीमार पौधे की तस्वीर लें और हमारा उन्नत एआई विजन मॉडल बीमारी की पहचान करेगा और उपचार की सिफारिश करेगा। आपको अपने जिले में खराब मौसम या अचानक कीटों के प्रकोप के लिए सक्रिय अलर्ट भी प्राप्त होंगे।",
    lp_how_4_title: "उपज की भविष्यवाणी करें और समझदारी से बेचें",
    lp_how_4_desc: "बाजार का अनुमान न लगाएं। अपने राज्य भर में वास्तविक समय के मंडी भाव तक पहुंचें। हमारे उन्नत पूर्वानुमान मॉडल आपके कुल फसल की मात्रा का अनुमान लगाते हैं, जिससे आपको बेहतर अनुबंधों पर बातचीत करने और अधिकतम लाभ के लिए सही समय पर बेचने में मदद मिलती है।",
    lp_ben_title: "AgriSmart क्यों चुनें?",
    lp_ben_subtitle: "अपनी पारंपरिक खेती के तरीकों को एक अत्यधिक अनुकूलित, डेटा-संचालित कृषि व्यवसाय में बदलें।",
    lp_ben_1_title: "उपज में 20% तक की वृद्धि",
    lp_ben_1_desc: "अनुमान लगाना बंद करें और जानना शुरू करें। डेटा-संचालित खेती सुनिश्चित करती है कि आपकी फसलों को ठीक उसी चीज़ की ज़रूरत है, जब उन्हें इसकी ज़रूरत होती है। बीमारी का शीघ्र पता लगने से मामूली संक्रमणों को आपकी पूरी फसल को नष्ट करने से रोका जा सकता है, जिससे आपकी कड़ी मेहनत सुरक्षित रहती है और समग्र उत्पादन में वृद्धि होती है।",
    lp_ben_2_title: "इनपुट लागत में भारी कमी",
    lp_ben_2_desc: "अत्यधिक खाद और पानी न केवल मिट्टी को नुकसान पहुंचाते हैं, वे आपके बटुए को भी खाली करते हैं। हमारी सटीक सैटेलाइट ट्रैकिंग और मौसम एकीकरण आपको ठीक से बताता है कि कब स्प्रे करना है और कब बचाना है, अनावश्यक रासायनिक और पानी के खर्चों में काफी कटौती करता है।",
    lp_ben_3_title: "अतिरिक्त आय के स्रोत खोलें",
    lp_ben_3_desc: "खेती फसल की कटाई से कहीं आगे जाती है। प्रासंगिक सरकारी सब्सिडी खोजें और लागू करें। साथ ही, AWD (वैकल्पिक गीलापन और सुखाने) जैसी टिकाऊ प्रथाओं को अपनाकर, आप अपनी पानी की बचत की पुष्टि कर सकते हैं और हमारे प्लेटफॉर्म के माध्यम से सीधे कार्बन क्रेडिट बेच सकते हैं।"""

pa_detailed = """    lp_how_title: "AgriSmart ਦੀ ਵਰਤੋਂ ਕਿਵੇਂ ਕਰੀਏ",
    lp_how_subtitle: "ਸ਼ੁਰੂਆਤੀ ਸੈੱਟਅੱਪ ਤੋਂ ਲੈ ਕੇ ਲਾਭਦਾਇਕ ਵਾਢੀ ਤੱਕ ਦਾ ਇੱਕ ਵਿਆਪਕ ਸਫ਼ਰ।",
    lp_how_1_title: "ਰਜਿਸਟਰ ਕਰੋ ਅਤੇ ਆਪਣਾ ਖੇਤ ਮੈਪ ਕਰੋ",
    lp_how_1_desc: "ਇੱਕ ਮਿੰਟ ਤੋਂ ਵੀ ਘੱਟ ਸਮੇਂ ਵਿੱਚ ਆਪਣਾ ਮੁਫਤ ਖਾਤਾ ਬਣਾਓ। ਸਾਡੇ ਏਕੀਕ੍ਰਿਤ ਨਕਸ਼ੇ ਇੰਟਰਫੇਸ ਦੀ ਵਰਤੋਂ ਕਰਦੇ ਹੋਏ, ਬਸ ਆਪਣੇ ਖੇਤ ਦੀਆਂ ਸੀਮਾਵਾਂ ਖਿੱਚੋ। ਇਹ ਸਾਡੇ ਸੈਟੇਲਾਈਟ ਕਨੈਕਸ਼ਨ ਨੂੰ ਸ਼ੁਰੂ ਕਰਦਾ ਹੈ, ਜੋ ਤੁਰੰਤ ਤੁਹਾਡੇ ਖਾਸ ਪਲਾਟ ਲਈ ਇਤਿਹਾਸਕ ਅਤੇ ਰੀਅਲ-ਟਾਈਮ ਬਨਸਪਤੀ ਸੂਚਕਾਂਕ (ਜਿਵੇਂ ਕਿ NDVI) ਪ੍ਰਾਪਤ ਕਰਦਾ ਹੈ।",
    lp_how_2_title: "ਸਿਹਤ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ ਅਤੇ ਖਰਚੇ ਦਰਜ ਕਰੋ",
    lp_how_2_desc: "ਕਾਗਜ਼ੀ ਨੋਟਬੁੱਕਾਂ ਤੋਂ ਅੱਗੇ ਵਧੋ। ਹਰ ਬੀਜ, ਖਾਦ, ਅਤੇ ਲੇਬਰ ਖਰਚੇ ਨੂੰ ਰਿਕਾਰਡ ਕਰਨ ਲਈ ਸਾਡੇ ਡਿਜੀਟਲ ਵਿੱਤੀ ਲੇਜ਼ਰ ਦੀ ਵਰਤੋਂ ਕਰੋ। ਇਸਦੇ ਨਾਲ ਹੀ, ਸਾਡੇ ਸਵੈਚਲਿਤ ਸੈਟੇਲਾਈਟ ਸਕੈਨ ਦੀ ਵਰਤੋਂ ਕਰਦੇ ਹੋਏ ਫਸਲ ਦੀ ਸਿਹਤ 'ਤੇ ਰੋਜ਼ਾਨਾ ਨਜ਼ਰ ਰੱਖੋ ਜੋ ਨਮੀ ਦੇ ਤਣਾਅ ਜਾਂ ਵਿਕਾਸ ਸੰਬੰਧੀ ਸਮੱਸਿਆਵਾਂ ਨੂੰ ਨੰਗੀ ਅੱਖ ਨਾਲ ਦਿਖਾਈ ਦੇਣ ਤੋਂ ਪਹਿਲਾਂ ਹੀ ਉਜਾਗਰ ਕਰਦੇ ਹਨ।",
    lp_how_3_title: "AI ਸੂਝ ਅਤੇ ਅਲਰਟ ਦਾ ਲਾਭ ਉਠਾਓ",
    lp_how_3_desc: "ਸਾਡਾ ਪਲੇਟਫਾਰਮ 24/7 ਕੰਮ ਕਰਦਾ ਹੈ। ਇੱਕ ਬਿਮਾਰ ਪੌਦੇ ਦੀ ਫੋਟੋ ਲਓ ਅਤੇ ਸਾਡਾ ਉੱਨਤ AI ਵਿਜ਼ਨ ਮਾਡਲ ਬਿਮਾਰੀ ਦੀ ਪਛਾਣ ਕਰੇਗਾ ਅਤੇ ਇਲਾਜ ਦੀ ਸਿਫ਼ਾਰਸ਼ ਕਰੇਗਾ। ਤੁਹਾਨੂੰ ਆਪਣੇ ਜ਼ਿਲ੍ਹੇ ਵਿੱਚ ਖਰਾਬ ਮੌਸਮ ਜਾਂ ਅਚਾਨਕ ਕੀੜਿਆਂ ਦੇ ਹਮਲੇ ਲਈ ਸਰਗਰਮ ਅਲਰਟ ਵੀ ਪ੍ਰਾਪਤ ਹੋਣਗੇ।",
    lp_how_4_title: "ਝਾੜ ਦੀ ਭਵਿੱਖਬਾਣੀ ਕਰੋ ਅਤੇ ਸਮਝਦਾਰੀ ਨਾਲ ਵੇਚੋ",
    lp_how_4_desc: "ਬਾਜ਼ਾਰ ਦਾ ਅੰਦਾਜ਼ਾ ਨਾ ਲਗਾਓ। ਆਪਣੇ ਪੂਰੇ ਰਾਜ ਵਿੱਚ ਰੀਅਲ-ਟਾਈਮ ਮੰਡੀ ਕੀਮਤਾਂ ਤੱਕ ਪਹੁੰਚ ਕਰੋ। ਸਾਡੇ ਉੱਨਤ ਪੂਰਵ-ਅਨੁਮਾਨ ਮਾਡਲ ਤੁਹਾਡੀ ਕੁੱਲ ਫਸਲ ਦੀ ਮਾਤਰਾ ਦਾ ਅੰਦਾਜ਼ਾ ਲਗਾਉਂਦੇ ਹਨ, ਜਿਸ ਨਾਲ ਤੁਹਾਨੂੰ ਬਿਹਤਰ ਇਕਰਾਰਨਾਮੇ ਕਰਨ ਅਤੇ ਵੱਧ ਤੋਂ ਵੱਧ ਮੁਨਾਫੇ ਲਈ ਸਹੀ ਸਮੇਂ 'ਤੇ ਵੇਚਣ ਵਿੱਚ ਮਦਦ ਮਿਲਦੀ ਹੈ।",
    lp_ben_title: "AgriSmart ਕਿਉਂ ਚੁਣੀਏ?",
    lp_ben_subtitle: "ਆਪਣੇ ਰਵਾਇਤੀ ਖੇਤੀ ਤਰੀਕਿਆਂ ਨੂੰ ਇੱਕ ਬਹੁਤ ਹੀ ਅਨੁਕੂਲਿਤ, ਡੇਟਾ-ਸੰਚਾਲਿਤ ਖੇਤੀਬਾੜੀ ਕਾਰੋਬਾਰ ਵਿੱਚ ਬਦਲੋ।",
    lp_ben_1_title: "ਝਾੜ ਵਿੱਚ 20% ਤੱਕ ਦਾ ਵਾਧਾ",
    lp_ben_1_desc: "ਅੰਦਾਜ਼ਾ ਲਗਾਉਣਾ ਬੰਦ ਕਰੋ ਅਤੇ ਜਾਣਨਾ ਸ਼ੁਰੂ ਕਰੋ। ਡੇਟਾ-ਸੰਚਾਲਿਤ ਖੇਤੀ ਇਹ ਯਕੀਨੀ ਬਣਾਉਂਦੀ ਹੈ ਕਿ ਤੁਹਾਡੀਆਂ ਫਸਲਾਂ ਨੂੰ ਬਿਲਕੁਲ ਉਹੀ ਮਿਲੇ ਜਿਸਦੀ ਉਹਨਾਂ ਨੂੰ ਲੋੜ ਹੈ, ਜਦੋਂ ਉਹਨਾਂ ਨੂੰ ਇਸਦੀ ਲੋੜ ਹੁੰਦੀ ਹੈ। ਬਿਮਾਰੀ ਦਾ ਜਲਦੀ ਪਤਾ ਲੱਗਣ ਨਾਲ ਮਾਮੂਲੀ ਇਨਫੈਕਸ਼ਨਾਂ ਨੂੰ ਤੁਹਾਡੀ ਪੂਰੀ ਫਸਲ ਨੂੰ ਤਬਾਹ ਕਰਨ ਤੋਂ ਰੋਕਿਆ ਜਾ ਸਕਦਾ ਹੈ, ਤੁਹਾਡੀ ਮਿਹਨਤ ਨੂੰ ਸੁਰੱਖਿਅਤ ਰੱਖਿਆ ਜਾ ਸਕਦਾ ਹੈ ਅਤੇ ਸਮੁੱਚੇ ਉਤਪਾਦਨ ਵਿੱਚ ਵਾਧਾ ਹੁੰਦਾ ਹੈ।",
    lp_ben_2_title: "ਇਨਪੁਟ ਲਾਗਤਾਂ ਵਿੱਚ ਭਾਰੀ ਕਮੀ",
    lp_ben_2_desc: "ਜ਼ਿਆਦਾ ਖਾਦ ਅਤੇ ਪਾਣੀ ਨਾ ਸਿਰਫ ਮਿੱਟੀ ਨੂੰ ਨੁਕਸਾਨ ਪਹੁੰਚਾਉਂਦੇ ਹਨ, ਬਲਕਿ ਇਹ ਤੁਹਾਡੇ ਬਟੂਏ ਨੂੰ ਵੀ ਖਾਲੀ ਕਰਦੇ ਹਨ। ਸਾਡੀ ਸਟੀਕ ਸੈਟੇਲਾਈਟ ਟਰੈਕਿੰਗ ਅਤੇ ਮੌਸਮ ਏਕੀਕਰਣ ਤੁਹਾਨੂੰ ਬਿਲਕੁਲ ਦੱਸਦਾ ਹੈ ਕਿ ਕਦੋਂ ਸਪਰੇਅ ਕਰਨਾ ਹੈ ਅਤੇ ਕਦੋਂ ਬਚਾਉਣਾ ਹੈ, ਬੇਲੋੜੇ ਰਸਾਇਣਕ ਅਤੇ ਪਾਣੀ ਦੇ ਖਰਚਿਆਂ ਵਿੱਚ ਕਾਫ਼ੀ ਕਟੌਤੀ ਕਰਦਾ ਹੈ।",
    lp_ben_3_title: "ਵਾਧੂ ਆਮਦਨ ਦੇ ਸਰੋਤ ਖੋਲ੍ਹੋ",
    lp_ben_3_desc: "ਖੇਤੀ ਵਾਢੀ ਤੋਂ ਕਿਤੇ ਅੱਗੇ ਜਾਂਦੀ ਹੈ। ਢੁਕਵੀਆਂ ਸਰਕਾਰੀ ਸਬਸਿਡੀਆਂ ਲੱਭੋ ਅਤੇ ਲਾਗੂ ਕਰੋ। ਇਸ ਤੋਂ ਇਲਾਵਾ, AWD (ਬਦਲਵੇਂ ਗਿੱਲੇ ਅਤੇ ਸੁਕਾਉਣ) ਵਰਗੇ ਟਿਕਾਊ ਅਭਿਆਸਾਂ ਨੂੰ ਅਪਣਾ ਕੇ, ਤੁਸੀਂ ਆਪਣੀ ਪਾਣੀ ਦੀ ਬਚਤ ਦੀ ਪੁਸ਼ਟੀ ਕਰ ਸਕਦੇ ਹੋ ਅਤੇ ਸਾਡੇ ਪਲੇਟਫਾਰਮ ਰਾਹੀਂ ਸਿੱਧੇ ਕਾਰਬਨ ਕ੍ਰੈਡਿਟ ਵੇਚ ਸਕਦੇ ਹੋ।" """

ml_detailed = """    lp_how_title: "AgriSmart എങ്ങനെ ഉപയോഗിക്കാം",
    lp_how_subtitle: "പ്രാരംഭ സജ്ജീകരണം മുതൽ ലാഭകരമായ വിളവെടുപ്പ് വരെയുള്ള സമഗ്രമായ യാത്ര.",
    lp_how_1_title: "രജിസ്റ്റർ ചെയ്ത് മാപ്പ് ചെയ്യുക",
    lp_how_1_desc: "ഒരു മിനിറ്റിനുള്ളിൽ നിങ്ങളുടെ സൗജന്യ അക്കൗണ്ട് സൃഷ്ടിക്കുക. ഞങ്ങളുടെ മാപ്പ് ഇന്റർഫേസ് ഉപയോഗിച്ച് നിങ്ങളുടെ ഫീൽഡിന്റെ അതിരുകൾ വരയ്ക്കുക. ഇത് നിങ്ങളുടെ സ്ഥലത്തിനായുള്ള ചരിത്രപരവും തത്സമയവുമായ NDVI ഡാറ്റ ഉടൻ ലഭ്യമാക്കുന്ന സാറ്റലൈറ്റ് കണക്ഷൻ ആരംഭിക്കുന്നു.",
    lp_how_2_title: "ആരോഗ്യം നിരീക്ഷിക്കുക, ചെലവുകൾ രേഖപ്പെടുത്തുക",
    lp_how_2_desc: "പേപ്പർ ബുക്കുകൾ ഒഴിവാക്കുക. ഓരോ വിത്ത്, വളം, തൊഴിൽ ചെലവുകൾ എന്നിവ രേഖപ്പെടുത്താൻ ഡിജിറ്റൽ സാമ്പത്തിക ലെഡ്ജർ ഉപയോഗിക്കുക. അതേസമയം, നഗ്നനേത്രങ്ങൾക്ക് കാണാൻ കഴിയുന്നതിന് മുമ്പ് തന്നെ വിളകളുടെ വളർച്ചയും ആരോഗ്യ പ്രശ്നങ്ങളും കണ്ടെത്താൻ സാറ്റലൈറ്റ് സ്കാനുകൾ നിങ്ങളെ സഹായിക്കുന്നു.",
    lp_how_3_title: "AI ഉൾക്കാഴ്ചകളും അലേർട്ടുകളും",
    lp_how_3_desc: "ഞങ്ങളുടെ പ്ലാറ്റ്ഫോം 24/7 പ്രവർത്തിക്കുന്നു. രോഗമുള്ള ചെടിയുടെ ഫോട്ടോ എടുക്കുക, ഞങ്ങളുടെ AI മോഡൽ രോഗം തിരിച്ചറിഞ്ഞ് ചികിത്സകൾ നിർദ്ദേശിക്കും. മോശം കാലാവസ്ഥയെക്കുറിച്ചും പെട്ടെന്നുള്ള കീടബാധയെക്കുറിച്ചും നിങ്ങൾക്ക് അലേർട്ടുകൾ ലഭിക്കും.",
    lp_how_4_title: "വിളവ് പ്രവചിക്കുക, ബുദ്ധിപൂർവ്വം വിൽക്കുക",
    lp_how_4_desc: "വിപണി ഊഹിക്കരുത്. നിങ്ങളുടെ സംസ്ഥാനത്തെ തത്സമയ മണ്ഡി വിലകൾ അറിയുക. നിങ്ങളുടെ മൊത്തം വിളവ് കണക്കാക്കാൻ ഞങ്ങളുടെ പ്രവചന മോഡലുകൾ സഹായിക്കുന്നു, ഇത് മികച്ച വിലയ്ക്ക് കൃത്യസമയത്ത് വിൽക്കാൻ നിങ്ങളെ പ്രാപ്തരാക്കുന്നു.",
    lp_ben_title: "എന്തുകൊണ്ട് AgriSmart തിരഞ്ഞെടുക്കണം?",
    lp_ben_subtitle: "നിങ്ങളുടെ പരമ്പരാഗത കൃഷി രീതികളെ വളരെ മികച്ചതും ഡാറ്റാ അധിഷ്ഠിതവുമായ ഒരു കാർഷിക ബിസിനസ്സാക്കി മാറ്റുക.",
    lp_ben_1_title: "വിളവിൽ 20% വരെ വർദ്ധനവ്",
    lp_ben_1_desc: "ഊഹിക്കുന്നത് നിർത്തി കൃത്യമായി അറിയാൻ തുടങ്ങുക. നിങ്ങളുടെ വിളകൾക്ക് ആവശ്യമുള്ളപ്പോൾ കൃത്യമായ അളവിൽ പോഷകങ്ങൾ ലഭിക്കുന്നുണ്ടെന്ന് ഉറപ്പാക്കുക. നേരത്തെയുള്ള രോഗനിർണ്ണയം നിങ്ങളുടെ വിളനാശം തടയുകയും മൊത്തം ഉൽപാദനം വർദ്ധിപ്പിക്കുകയും ചെയ്യുന്നു.",
    lp_ben_2_title: "ഇൻപുട്ട് ചെലവുകൾ ഗണ്യമായി കുറയ്ക്കുക",
    lp_ben_2_desc: "അമിതമായി വളം ഇടുന്നതും നനയ്ക്കുന്നതും മണ്ണിനെ ദോഷകരമായി ബാധിക്കുക മാത്രമല്ല, നിങ്ങളുടെ പണം നഷ്ടപ്പെടുത്തുകയും ചെയ്യുന്നു. കൃത്യമായ സാറ്റലൈറ്റ്, കാലാവസ്ഥാ ട്രാക്കിംഗ് എപ്പോൾ സ്പ്രേ ചെയ്യണമെന്നും എപ്പോൾ ലാഭിക്കണമെന്നും നിങ്ങളോട് പറയുന്നു.",
    lp_ben_3_title: "അധിക വരുമാന മാർഗ്ഗങ്ങൾ കണ്ടെത്തുക",
    lp_ben_3_desc: "കൃഷി എന്നത് വിളവെടുപ്പിനപ്പുറമാണ്. പ്രസക്തമായ സർക്കാർ സബ്സിഡികൾ കണ്ടെത്തി അപേക്ഷിക്കുക. AWD പോലുള്ള സുസ്ഥിര രീതികൾ സ്വീകരിക്കുന്നതിലൂടെ, നിങ്ങൾക്ക് കാർബൺ ക്രെഡിറ്റുകൾ വഴി കൂടുതൽ വരുമാനം നേടാനാകും."""


def replace_chunk(content, lang_key, replacement):
    pattern = rf"(  {lang_key}: {{.*?)(    lp_how_title:.*?    lp_ben_3_desc: .*?\n)(.*?  }},)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"Could not find match for {lang_key}")
        return content
    return content[:match.start(2)] + replacement + "\n" + content[match.end(2):]

content = replace_chunk(content, "en", en_detailed)
content = replace_chunk(content, "hi", hi_detailed)
content = replace_chunk(content, "pa", pa_detailed)
content = replace_chunk(content, "ml", ml_detailed)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated beautifully.")
