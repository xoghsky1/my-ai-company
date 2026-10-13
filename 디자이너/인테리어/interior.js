// 인테리어 데이터 (디자이너 작성). 뷰어가 이 파일을 읽어 마감재·가구·옵션·제안안을 그린다.
// 좌표는 model.json과 같다: x 오른쪽, y 아래쪽(평면도 기준), 단위 m. 가구 크기는 mm.
// 기준 문서: 디자이너/2026-10-12-2단계-인테리어조합-디자인.md, 디자이너/2026-10-12-3단계-배치3안-디자인.md
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
    face: [3.56, 5.401, 3.56, 7.801, 'w'],   // 600 타일 정확히 4장, 가운데 줄눈이 TV 중심(y 6.0)
    color: '#EDEBE7', grout: '#CFCBC4', tileW: 0.6, tileH: 1.2,
  },

  // 가구·가전·소품 목록
  // kind: 뷰어의 모양 종류 / at: 중심 [x, y] / size: [w, d, h] mm
  // rot: 도. 0이면 w가 x축(오른쪽), d가 y축(아래쪽) 방향이고 등판(뒷면)이 위쪽(y 작은 쪽). 시계 방향으로 돈다.
  //   예: 90이면 등판이 오른쪽 벽, 180이면 아래쪽 벽, 270이면 왼쪽 벽을 향한다. 침대는 머리판이 w의 왼쪽 끝.
  // group: 목록 묶음 / builtin: 분양 기본 품목(끌 수 없음) / flat: 바닥에 까는 것(겹침·동선 검사 제외)
  // mount: 벽에 거는 높이(m, 바닥 겹침 검사 제외) / front: 앞에 비워야 할 거리(mm, QA 검사)
  furniture: [
    // 분양 기본 (평면도에 그려진 것, 위치 추정)
    { id: 'counter-a', kind: 'counter', group: '기본', name: '주방 상판 (세로)', room: '주방/식당', size: [600, 2270, 900], at: [3.161, 1.454], rot: 0, builtin: true,
      colors: { body: '#F4F2EE', top: '#E9E6E0' } },
    { id: 'counter-b', kind: 'counter', group: '기본', name: '주방 상판 (개수대)', room: '주방/식당', size: [1180, 620, 900], at: [4.108, 0.629], rot: 0, builtin: true,
      colors: { body: '#F4F2EE', top: '#E9E6E0' } },
    { id: 'shoe', kind: 'cabinet', group: '기본', name: '현관 신발장', room: '현관', size: [1290, 330, 2200], at: [6.721, 3.46], rot: 270, builtin: true, front: 600,
      colors: { body: '#F5F3EF', line: '#DDD8D0' } },
    { id: 'bathtub', kind: 'bathtub', group: '기본', name: '욕조', room: '욕실1', size: [1310, 620, 550], at: [8.756, 3.595], rot: 0, builtin: true,
      colors: { body: '#FAFAF8', inner: '#EEF1F2' } },

    // 2단계 필수 가구
    { id: 'bed', kind: 'bed', group: '가구', name: '퀸 침대', room: '안방', size: [2000, 1500, 900], at: [1.216, 6.788], rot: 0, front: 500,
      colors: { frame: '#EDE9E3', mattress: '#FFFFFF', head: '#E2DDD5' } },
    { id: 'crib', kind: 'crib', group: '가구', name: '아기침대', room: '아기방', size: [700, 1300, 900], at: [9.111, 6.161], rot: 0,
      colors: { frame: '#F3EFE8', mattress: '#FFFFFF' } },
    { id: 'dresser', kind: 'cabinet', group: '가구', name: '기저귀 갈이 서랍장', room: '아기방', size: [1000, 500, 950], at: [7.279, 7.261], rot: 270, front: 600,
      colors: { body: '#F5F3EF', line: '#D9D4CC' } },
    { id: 'dining', kind: 'dining', group: '가구', name: '식탁 4인 (의자 포함)', room: '주방/식당', size: [1200, 1700, 750], at: [5.556, 3.63], rot: 0, front: 600,
      colors: { top: '#F4F2EE', leg: '#D8CFC2', chair: '#E9E4DC' } },
    { id: 'sofa', kind: 'sofa', group: '가구', name: '거실 3인 소파', room: '거실', size: [2000, 850, 780], at: [6.407, 6.601], rot: 90, front: 500,
      colors: { body: '#E7E3DC', cushion: '#F3F1EC' } },

    // 3단계 추가 가구
    { id: 'nightstand-1', kind: 'cabinet', group: '가구', name: '협탁 1', room: '안방', size: [450, 350, 500], at: [0.446, 5.765], rot: 0,
      colors: { body: '#EFEBE5', line: '#D9D4CC' } },
    { id: 'nightstand-2', kind: 'cabinet', group: '가구', name: '협탁 2', room: '안방', size: [450, 350, 500], at: [0.446, 7.837], rot: 180,
      colors: { body: '#EFEBE5', line: '#D9D4CC' } },
    { id: 'tvstand', kind: 'cabinet', group: '가구', name: '낮은 TV장', room: '거실', size: [1800, 400, 450], at: [3.768, 6.601], rot: 270, front: 500,
      colors: { body: '#F5F3EF', line: '#DDD8D0' } },
    { id: 'lowshelf', kind: 'shelf', group: '가구', name: '아기 낮은 책장', room: '거실', size: [1600, 300, 600], at: [3.718, 6.601], rot: 270, front: 500,
      colors: { body: '#F3EFE8', line: '#DDD5C8' } },
    { id: 'nursing', kind: 'armchair', group: '가구', name: '수유 의자', room: '아기방', size: [700, 750, 900], at: [9.021, 7.646], rot: 90, front: 500,
      colors: { body: '#EDE8E0', cushion: '#F6F3EE' } },
    { id: 'wardrobe-1', kind: 'wardrobe', group: '가구', name: '옷방 시스템 선반 (왼쪽 벽)', room: '옷방', size: [2530, 500, 2000], at: [0.47, 1.683], rot: 270, front: 600,
      colors: { body: '#F2EFEA', line: '#D9D3C9' } },
    { id: 'wardrobe-2', kind: 'wardrobe', group: '가구', name: '옷방 시스템 선반 (오른쪽 벽)', room: '옷방', size: [1430, 500, 2000], at: [2.412, 1.094], rot: 90, front: 600,
      colors: { body: '#F2EFEA', line: '#D9D3C9' } },
    { id: 'mirror', kind: 'mirror', group: '소품', name: '전신 거울', room: '옷방', size: [500, 60, 1700], at: [1.43, 2.977], rot: 180,
      colors: { frame: '#E2DDD5', glass: '#DCE6EC' } },
    { id: 'cafe', kind: 'cabinet', group: '가구', name: '홈카페 수납장', room: '주방/식당', size: [1200, 400, 900], at: [6.234, 3.465], rot: 90, front: 600,
      colors: { body: '#F5F3EF', line: '#DDD8D0' } },

    // 가전
    { id: 'fridge', kind: 'fridge', group: '가전', name: '4도어 냉장고', room: '주방/식당', size: [912, 930, 1800], at: [3.331, 3.146], rot: 270, front: 900,
      colors: { body: '#F1F0EC', line: '#D7D5CF' } },
    { id: 'washer', kind: 'washer', group: '가전', name: '세탁기·건조기 (직렬)', room: '다용도실', size: [700, 760, 1900], at: [6.043, 1.458], rot: 90, front: 700,
      colors: { body: '#F4F4F2', door: '#C9CDD1' } },
    { id: 'tv', kind: 'tv', group: '가전', name: '65인치 TV (벽걸이)', room: '거실', size: [1450, 60, 830], at: [3.592, 6.601], rot: 270, mount: 0.65,
      colors: { body: '#2A2C2E' } },
    { id: 'aircon', kind: 'aircon', group: '가전', name: '스탠드 에어컨', room: '거실', size: [380, 380, 1800], at: [3.752, 8.175], rot: 270,
      colors: { body: '#F7F7F5', line: '#D9DCDF' } },
    { id: 'aircon-wall', kind: 'aircon-wall', group: '가전', name: '안방 벽걸이 에어컨', room: '안방', size: [900, 230, 300], at: [3.282, 6.601], rot: 90, mount: 1.95,
      colors: { body: '#F7F7F5' } },
    { id: 'purifier', kind: 'purifier', group: '가전', name: '공기청정기', room: '아기방', size: [350, 350, 700], at: [7.239, 6.436], rot: 0,
      colors: { body: '#F6F6F4', line: '#D7DADC' } },

    { id: 'robot', kind: 'cabinet', group: '가전', name: '로봇청소기 스테이션', room: '주방/식당', size: [350, 420, 450], at: [3.163, 3.905], rot: 270,
      colors: { body: '#F2F2F0', line: '#CFD2D4' } },

    // 창호 (소품 개수에서 제외). mount 0 = 바닥 겹침 검사 제외. 줄 없는 레일(영아 안전)
    { id: 'curtain-living', kind: 'curtain', group: '창호', name: '거실 커튼 (암막 린넨 + 속지)', room: '거실', size: [2450, 100, 2280], at: [5.218, 8.559], rot: 0, mount: 0,
      colors: { body: '#EDE8E0', fold: '#E2DBD0', sheer: '#FBFAF7', rail: '#E2DDD5' } },
    { id: 'curtain-master', kind: 'curtain', group: '창호', name: '안방 발코니 창 암막 커튼', room: '안방', size: [1540, 100, 2280], at: [2.605, 7.899], rot: 0, mount: 0,
      colors: { body: '#EDE8E0', fold: '#E2DBD0', rail: '#E2DDD5' } },
    { id: 'curtain-baby', kind: 'curtain', group: '창호', name: '아기방 암막 커튼', room: '아기방', size: [1340, 100, 2280], at: [8.14, 8.559], rot: 0, mount: 0,
      colors: { body: '#EDE8E0', fold: '#E2DBD0', sheer: '#FBFAF7', rail: '#E2DDD5' } },

    // 소품
    { id: 'rug', kind: 'rug', group: '소품', name: '러그 2000×1400', room: '거실', size: [2000, 1400, 10], at: [4.84, 6.601], rot: 90, flat: true,
      colors: { body: '#ECE7DF', border: '#DCD5CA' } },
    { id: 'playmat', kind: 'rug', group: '소품', name: '아기 놀이매트', room: '거실', size: [2000, 1400, 40], at: [4.95, 6.601], rot: 90, flat: true,
      colors: { body: '#F4F1EC', border: '#E3DDD3' } },
    { id: 'lamp', kind: 'lamp', group: '소품', name: '플로어 스탠드', room: '거실', size: [350, 350, 1600], at: [6.655, 8.086], rot: 0,
      colors: { body: '#E8E4DE', shade: '#FBF8F2' } },
    { id: 'plant', kind: 'plant', group: '소품', name: '대형 화분 (떡갈고무나무)', room: '거실', size: [360, 360, 1300], at: [6.665, 8.031], rot: 0,
      colors: { pot: '#E9E5DE', leaf: '#9DAA8E' } },
    { id: 'plant-2', kind: 'plant', group: '소품', name: '소형 화분', room: '주방/식당', size: [300, 300, 700], at: [3.74, 0.495], rot: 0, mount: 0.9,
      colors: { pot: '#E9E5DE', leaf: '#A7B39A' } },
  ],

  // 처음 열 때 적용되는 기본 조합 (지울 수 없음). 목록에 없는 가구는 숨김.
  preset: {
    name: '화이트 미니멀 기본',
    floors: { '거실': 'white-oak', '주방/식당': 'white-oak', '안방': 'white-oak', '아기방': 'white-oak', '옷방': 'white-oak', '현관': 'white-porcelain', '복도': 'white-oak' },
    walls: { '거실': 'pure-white', '주방/식당': 'pure-white', '안방': 'pure-white', '아기방': 'pure-white', '옷방': 'pure-white', '현관': 'pure-white', '복도': 'pure-white' },
    artWall: false,
    show: ['counter-a', 'counter-b', 'shoe', 'bathtub', 'bed', 'crib', 'dresser', 'dining', 'sofa'],
  },

  // 팀 제안 3안 (3단계). show = 보이는 가구, place = 기본 자리에서 바꾼 위치·방향
  proposals: [
    {
      id: 'A', name: 'A안 · 놀이 거실',
      summary: 'TV 없이 거실 바닥을 아기 놀이 공간으로 비운 안. 아트월 자리에 낮은 책장(600), 가운데 놀이매트, 소파는 아기방 쪽 벽. 아이가 크면 책장을 TV장으로 바꿔 B안으로 넘어갈 수 있다.',
      floors: { '거실': 'white-oak', '주방/식당': 'white-oak', '안방': 'white-oak', '아기방': 'white-oak', '옷방': 'white-oak', '현관': 'white-porcelain', '복도': 'white-oak' },
      walls: { '거실': 'pure-white', '주방/식당': 'pure-white', '안방': 'pure-white', '아기방': 'pure-white', '옷방': 'pure-white', '현관': 'pure-white', '복도': 'pure-white' },
      artWall: false,
      show: ['counter-a', 'counter-b', 'shoe', 'bathtub', 'bed', 'nightstand-1', 'crib', 'dresser', 'nursing', 'dining', 'sofa', 'lowshelf', 'playmat', 'lamp', 'plant-2',
             'fridge', 'washer', 'robot', 'aircon', 'aircon-wall', 'purifier', 'wardrobe-1', 'wardrobe-2', 'mirror',
             'curtain-living', 'curtain-master', 'curtain-baby'],
      place: {},
    },
    {
      id: 'B', name: 'B안 · 정석 TV 거실',
      summary: '아트월 대형타일(유상, 타일 4장 폭)에 65인치 벽걸이 TV와 낮은 TV장, 맞은편 소파와 러그. 바닥을 웜 그레이로 내려 흰 가구가 떠 보이게 한 차분한 호텔형.',
      floors: { '거실': 'warm-gray', '주방/식당': 'warm-gray', '안방': 'warm-gray', '아기방': 'warm-gray', '옷방': 'warm-gray', '현관': 'white-porcelain', '복도': 'warm-gray' },
      walls: { '거실': 'warm-white', '주방/식당': 'warm-white', '안방': 'warm-white', '아기방': 'warm-white', '옷방': 'warm-white', '현관': 'warm-white', '복도': 'warm-white' },
      artWall: true,
      show: ['counter-a', 'counter-b', 'shoe', 'bathtub', 'bed', 'nightstand-1', 'crib', 'dresser', 'nursing', 'dining', 'sofa', 'tvstand', 'tv', 'rug', 'plant',
             'fridge', 'washer', 'robot', 'aircon', 'aircon-wall', 'purifier', 'wardrobe-1', 'wardrobe-2', 'mirror',
             'curtain-living', 'curtain-master', 'curtain-baby'],
      // 축척을 고친 뒤 거실 폭이 4.4m라, 소파를 벽에서 0.25m 띄워 TV 거리를 65인치 기준(2.6m 이내)에 맞춘다
      place: {
        sofa: { at: [6.157, 6.601], rot: 90 },
      },
    },
    {
      id: 'C', name: 'C안 · 신생아 동침',
      summary: '첫해 새벽 수유를 위해 부부 퀸 침대와 아기침대를 침실2(뷰어의 아기방)에 붙여 함께 자는 안. 안방(침실1)은 기저귀 갈이 서랍장·수유 의자·놀이매트를 둔 낮 시간 방. 거실은 소파·러그·낮은 장으로 단정하게, TV는 나중에.',
      floors: { '거실': 'white-oak', '주방/식당': 'white-oak', '안방': 'white-oak', '아기방': 'white-oak', '옷방': 'white-oak', '현관': 'white-porcelain', '복도': 'white-oak' },
      walls: { '거실': 'warm-white', '주방/식당': 'warm-white', '안방': 'warm-white', '아기방': 'sage-white', '옷방': 'warm-white', '현관': 'warm-white', '복도': 'warm-white' },
      artWall: false,
      show: ['counter-a', 'counter-b', 'shoe', 'bathtub', 'bed', 'crib', 'dresser', 'nursing', 'playmat', 'dining', 'sofa', 'tvstand', 'rug', 'lamp', 'plant-2',
             'fridge', 'washer', 'robot', 'aircon', 'aircon-wall', 'purifier', 'wardrobe-1', 'wardrobe-2', 'mirror',
             'curtain-living', 'curtain-master', 'curtain-baby'],
      place: {
        bed: { at: [8.705, 7.375], rot: 270 },   // 오른쪽 벽·창 쪽 벽에 붙임
        crib: { at: [7.60, 7.40], rot: 0 },      // 침대 왼쪽에 바로 붙임, 창에서 0.33m
        purifier: { at: [9.285, 5.501], rot: 0 },
        dresser: { at: [0.456, 6.601], rot: 270 },
        nursing: { at: [2.915, 7.041], rot: 90 },
        playmat: { at: [1.606, 6.601], rot: 90 },
      },
    },
  ],
}
