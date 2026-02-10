import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "@/hooks/useTranslation";
import MapView from "./MapView";

export function MyField() {
  const { t } = useTranslation();
  const [selectedCrop, setSelectedCrop] = useState("");
  const [selectedIrrigation, setSelectedIrrigation] = useState("");
  const [selectedSoil, setSelectedSoil] = useState("");

  const crops = [
    { value: "rice", label: "Rice / चावल / അരി" },
    { value: "coconut", label: "Coconut / नारियल / തേങ്ങ" },
    { value: "banana", label: "Banana / केला / വാഴപ്പഴം" },
    { value: "black_pepper", label: "Black Pepper / काली मिर्च / കുരുമുളക്" },
    { value: "cardamom", label: "Cardamom / इलायची / ഏലക്ക" },
    { value: "coffee", label: "Coffee / कॉफ़ी / കോഫി" },
    { value: "tea", label: "Tea / चाय / ചായ" },
    { value: "rubber", label: "Rubber / रबड़ / റബ്ബർ" },
    { value: "arecanut", label: "Arecanut / सुपारी / അടക്ക" },
    { value: "tapioca", label: "Tapioca / कसावा / കപ്പ" },
    { value: "ginger", label: "Ginger / अदरक / ഇഞ്ചി" },
    { value: "turmeric", label: "Turmeric / हल्दी / മഞ്ഞൾ" },
  ];

  const soilTypes = [
    { value: "loamy", label: "Loamy / दोमट / ലോമി" },
    { value: "clay", label: "Clay / मिट्टी / മണ്ണ്" },
    { value: "laterite", label: "Laterite / लेटराइट / ലാറ്ററൈറ്റ്" },
    { value: "sandy", label: "Sandy / रेतीला / മണൽ" },
    { value: "peaty", label: "Peaty / पीटी / പീറ്റി" },
  ];

  const irrigationTypes = [
    { value: "drip", label: "Drip / ड्रिप / ഡ്രിപ്പ്" },
    { value: "sprinkler", label: "Sprinkler / स्प्रिंकलर / സ്‌പ്രിങ്ക്ലർ" },
    { value: "flood", label: "Flood / बाढ़ / വെള്ളപ്പൊക്കം" },
    { value: "manual", label: "Manual / मैनुअल / മാനുവൽ" },
    { value: "basin", label: "Basin / बेसिन / ബേസിൻ" },
  ];

  return (
    <div className="relative h-[calc(100vh-4rem)] w-full overflow-hidden flex flex-col lg:flex-row">
      {/* Full Screen Map */}
      <div className="absolute inset-0 z-0">
        <MapView
          cropType={selectedCrop}
          soilType={selectedSoil}
          irrigationType={selectedIrrigation}
        />
      </div>

      {/* Floating Control Panel (Desktop: Right Side, Mobile: Bottom Sheet style) */}
      <div className="absolute right-0 top-0 bottom-0 pointer-events-none p-4 z-10 w-full lg:w-[400px] flex flex-col justify-end lg:justify-start">
        <div className="pointer-events-auto bg-background/95 backdrop-blur-sm border shadow-xl rounded-xl p-6 overflow-y-auto max-h-[50vh] lg:max-h-full">
          <h1 className="text-2xl font-bold text-foreground mb-4">
            {t("my_field")}
          </h1>
          <p className="text-sm text-muted-foreground mb-6">
            Draw your field boundary on the map to get started. Select your crop details below for accurate analysis.
          </p>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">{t("crop_type")}</label>
              <Select value={selectedCrop} onValueChange={setSelectedCrop}>
                <SelectTrigger data-testid="select-crop-type" className="bg-background">
                  <SelectValue placeholder={t("select_crop")} />
                </SelectTrigger>
                <SelectContent>
                  {crops.map((crop) => (
                    <SelectItem key={crop.value} value={crop.value}>{crop.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">{t("soil_type")}</label>
              <Select value={selectedSoil} onValueChange={setSelectedSoil}>
                <SelectTrigger data-testid="select-soil-type" className="bg-background">
                  <SelectValue placeholder={t("soil_placeholder")} />
                </SelectTrigger>
                <SelectContent>
                  {soilTypes.map((soil) => (
                    <SelectItem key={soil.value} value={soil.value}>{soil.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">{t("irrigation_type")}</label>
              <Select value={selectedIrrigation} onValueChange={setSelectedIrrigation}>
                <SelectTrigger data-testid="select-irrigation-type" className="bg-background">
                  <SelectValue placeholder={t("irrigation_placeholder")} />
                </SelectTrigger>
                <SelectContent>
                  {irrigationTypes.map((item) => (
                    <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
