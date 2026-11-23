# 하우머치노트 (howmuchnote.com)

생활 비용 정리 글과 급여·대출·부동산·생활 계산기를 모은 정적 사이트입니다.

- 계산기 설명·FAQ: `data/calcs/{slug}.json`
- 계산기 입력 화면과 계산 로직: `src/calcs/{slug}.html`, `src/calcs/{slug}.js`
- 공통 스타일·스크립트: `src/assets/`
- 비용 글: `data/posts/{slug}.json`, 글 이미지: `src/images/{slug}/01.jpg` (`python3 tools/title2.py`로 생성)
- 글 기록: `data/posts.csv`
- 사이트 설정(이름, 도메인, 광고 코드, 카테고리): `data/config.json`

## 빌드

```
python3 build.py
```

`site/` 폴더에 전체 사이트가 만들어집니다. Cloudflare Pages 설정은 빌드 명령 `python3 build.py`, 출력 디렉터리 `site`입니다.
