export { };

declare global {
    interface SpeechRecognitionEvent extends Event {
        results: SpeechRecognitionResultList;
        resultIndex: number;
        interpretation: any;
    }

    interface SpeechRecognitionResultList {
        length: number;
        item(index: number): SpeechRecognitionResult;
        [index: number]: SpeechRecognitionResult;
    }

    interface SpeechRecognitionResult {
        length: number;
        item(index: number): SpeechRecognitionAlternative;
        [index: number]: SpeechRecognitionAlternative;
        isFinal: boolean;
    }

    interface SpeechRecognitionAlternative {
        transcript: string;
        confidence: number;
    }

    interface SpeechRecognition extends EventTarget {
        continuous: boolean;
        interimResults: boolean;
        lang: string;
        start(): void;
        stop(): void;
        abort(): void;
        onresult: (event: SpeechRecognitionEvent) => void;
        onerror: (event: any) => void;
        onend: (event: any) => void;
    }

    var SpeechRecognition: {
        new(): SpeechRecognition;
    };
    var webkitSpeechRecognition: {
        new(): SpeechRecognition;
    };
}

declare module 'leaflet-geosearch';
