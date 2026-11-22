// 근로기준법 제55조, 시행령 제30조: 주 15시간 이상 개근 시 1일 소정근로시간분 유급휴일
const WEEKS=365/7/12; // 월 평균 주 수 약 4.345
C.onCalc(()=>{
  const w=C.num('wage'),h=C.num('hours');
  if(w<=0||h<=0){C.show('res','<p class="msg">시급과 근무시간을 입력해 주세요.</p>');return}
  const ok=h>=15;
  const hh=Math.min(h,40)/40*8;
  const hol=ok?w*hh:0;
  const week=w*h+hol;
  const monthHours=(h+(ok?hh:0))*WEEKS;
  const min=w<10320?'<p class="msg">입력한 시급이 2026년 최저임금(10,320원)보다 낮습니다.</p>':'';
  C.show('res',`<div class="big">1주 주휴수당<b>${C.won(hol)}</b></div>${min}
  ${ok?'':'<p class="msg">1주 소정근로시간이 15시간 미만이면 주휴수당이 발생하지 않습니다.</p>'}
  ${C.rows([
    ['주휴시간',`${hh.toFixed(1).replace(/\.0$/,'')}시간${ok?'':' (미발생)'}`],
    ['1주 근무 급여',C.won(w*h)],
    ['1주 주휴수당',C.won(hol)],
    ['1주 총 급여',C.won(week),'sum'],
    ['월 환산 유급시간',`약 ${monthHours.toFixed(1)}시간`],
    ['월 예상 급여 (주휴 포함)',C.won(week*WEEKS),'sum']])}
  <p class="how">주휴시간 = (1주 소정근로시간 ÷ 40) × 8시간, 최대 8시간입니다. 월 급여는 한 달 평균 주 수(365 ÷ 7 ÷ 12 ≈ 4.345주)를 곱해 계산했습니다.</p>`);
});
