// 2단계 인테리어 데이터 (디자이너 작성). 뷰어가 이 파일을 읽어 마감재·가구·옵션을 그린다.
// 좌표는 model.json과 같다: x 오른쪽, y 아래쪽(평면도 기준), 단위 m. 가구 크기는 mm.
// 기준 문서: 디자이너/2026-10-12-2단계-인테리어조합-디자인.md
window.APT_INTERIOR = {
  style: '화이트 미니멀',

  // 바닥재: pattern = wood(마루 판), tile(정사각 타일). size = 판 폭 또는 타일 한 변(m)
  floors: [
    { id: 'white-oak', name: '화이트 오크 마루', color: '#E6D8C3', grain: '#D9C8AF', pattern: 'wood', size: 0.19 },
    { id: 'light-ash', name: '라이트 애쉬 마루', color: '#EDE6DA', grain: '#E0D6C6', pattern: 'wood', size: 0.19 },
    { id: 'warm-gray', name: '웜 그레이 마루', color: '#CFC6BA', grain: '#C1B7A9', pattern: 'wood', size: 0.19 },
    { id: 'white-porcelain', name: '화이트 포세린 타일 600', color: '#F2F1EE', grain: '#D6D4CF', pattern: 'tile', size: 0.6 },
    { id: 'light-gray-tile', name: '라이트 그레이 타일 600', color: '#DAD9D5', grain: '#BDBBB6', pattern: 'tile', size: 0.6 },
  ],

  walls: [
    { id: 'pure-white', name: '퓨어 화이트', color: '#FAFAF8' },
    { id: 'warm-white', name: '웜 화이트', color: '#F4F0E8' },
    { id: 'light-gray', name: '라이트 그레이', color: '#E4E4E2' },
    { id: 'sage-white', name: '세이지 화이트', color: '#E8ECE4' },
  ],

  // 마감재를 바꿀 수 있는 방 (욕실·다용도실·발코니·실외기실 제외)
  finishRooms: ['거실', '주방/식당', '안방', '아기방', '옷방', '현관', '복도'],

  // 유상 옵션: 거실 아트월 대형타일. 거실 왼쪽 벽(안방과 맞닿은 벽)의 거실 쪽 면.
  artWall: {
    name: '거실 아트월 대형타일 (600×1200)',
    room: '거실',
    face: [3.236, 4.726, 3.236, 7.617, 'w'],
    color: '#EDEBE7', grout: '#CFCBC4', tileW: 0.6, tileH: 1.2,
  },

  // 가구: kind는 뷰어의 모양 종류. at = 중심 [x, y], size = [w, d, h] mm.
  // rot = 도. 0이면 w가 x축(오른쪽), d가 y축(아래쪽) 방향이고 등판(뒷면)이 위쪽(y 작은 쪽). 시계 방향으로 돈다.
  // 예: 90이면 등판이 오른쪽 벽, 270이면 왼쪽 벽을 향한다. 침대는 머리판이 w의 왼쪽 끝.
  furniture: [
    { id: 'bed', kind: 'bed', name: '안방 퀸 침대', room: '안방', size: [2000, 1500, 1000], at: [1.2, 6.05], rot: 0,
      colors: { frame: '#EDE9E3', mattress: '#FFFFFF', head: '#E2DDD5' } },
    { id: 'crib', kind: 'crib', name: '아기침대', room: '아기방', size: [700, 1300, 900], at: [8.246, 5.6], rot: 0,
      colors: { frame: '#F3EFE8', mattress: '#FFFFFF' } },
    { id: 'dresser', kind: 'cabinet', name: '아기방 수납장', room: '아기방', size: [1000, 450, 1200], at: [6.626, 6.6], rot: 270,
      colors: { body: '#F5F3EF', line: '#D9D4CC' } },
    { id: 'dining', kind: 'dining', name: '식탁 4인 (의자 포함)', room: '주방/식당', size: [1200, 1700, 750], at: [4.6, 2.9], rot: 0,
      colors: { top: '#F4F2EE', leg: '#D8CFC2', chair: '#E9E4DC' } },
    { id: 'sofa', kind: 'sofa', name: '거실 3인 소파', room: '거실', size: [2100, 900, 800], at: [5.737, 6.15], rot: 90,
      colors: { body: '#E7E3DC', cushion: '#F3F1EC' } },
  ],

  // 처음 열 때 적용되는 기본 조합 (지울 수 없음)
  preset: {
    name: '화이트 미니멀 기본',
    floors: { '거실': 'white-oak', '주방/식당': 'white-oak', '안방': 'white-oak', '아기방': 'white-oak', '옷방': 'white-oak', '현관': 'white-porcelain', '복도': 'white-oak' },
    walls: { '거실': 'pure-white', '주방/식당': 'pure-white', '안방': 'pure-white', '아기방': 'pure-white', '옷방': 'pure-white', '현관': 'pure-white', '복도': 'pure-white' },
    artWall: false,
  },
}
