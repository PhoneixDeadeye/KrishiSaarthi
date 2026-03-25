export { };

declare global {
    interface SpeechRecognitionEvent extends Event {
        results: SpeechRecognitionResultList;
        resultIndex: number;
        interpretation: unknown;
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
        onstart: ((event: Event) => void) | null;
        onresult: ((event: SpeechRecognitionEvent) => void) | null;
        onerror: ((event: Event) => void) | null;
        onend: ((event: Event) => void) | null;
        __shouldKeepRecording?: boolean;
    }

    var SpeechRecognition: {
        new(): SpeechRecognition;
    };
    var webkitSpeechRecognition: {
        new(): SpeechRecognition;
    };
}

declare module 'leaflet-geosearch';
