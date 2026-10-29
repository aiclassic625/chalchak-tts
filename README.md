# 찰칵중국어 TTS 서버

Edge TTS (Xiaoxiao/Yunxi) 로컬·배포용 서버.

## 로컬
```bash
cd tts_server
./run.sh
# http://127.0.0.1:8766/health
```

## 배포
- Render: 이 폴더를 GitHub에 올리고 `render.yaml`로 Blueprint 배포
- Docker: `docker build -t chalchak-tts . && docker run -p 8766:8766 chalchak-tts`
- 배포 후 앱의 `window.CK_TTS_BASE`를 `https://<서버주소>`로 변경

Edge TTS는 비공식 미리듣기/프로토타입용입니다. App Store 장기 운영은 Azure Speech를 권장합니다.
