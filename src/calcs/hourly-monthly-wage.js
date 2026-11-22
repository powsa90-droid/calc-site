// 월 유급시간 = (1주 소정근로시간 + 주휴시간) × (365 ÷ 7 ÷ 12), 주 40시간이면 209시간
const MIN=10320;
function monthHours(h){const hol=h>=15?Math.min(h,40)/40*8:0;return{hol,mh:Math.round((h+hol)*365/7/12)}}
document.querySelectorAll('input[name="dir"]').forEach(el=>el.addEventListener('change',()=>{
  const h=C.radio('dir')==='h2m';C.$('#amtL').textContent=h?'시급':'월급 (세전, 기본급+고정수당)';C.$('#amt').value=h?'10,320':'2,500,000';
}));
C.onCalc(()=>{
  const a=C.num('amt'),h=C.num('hours');
  if(a<=0||h<=0){C.show('res','<p class="msg">금액과 근무시간을 입력해 주세요.</p>');return}
  const {hol,mh}=monthHours(Math.min(h,40));
  const h2m=C.radio('dir')==='h2m';
  const hourly=h2m?a:a/mh,monthly=h2m?a*mh:a;
  const low=hourly<MIN?`<p class="msg">시급이 2026년 최저임금 ${C.fmt(MIN)}원보다 ${C.fmt(MIN-hourly)}원 낮습니다.</p>`:'';
  C.show('res',`<div class="big">${h2m?'월급 (주휴수당 포함)':'환산 시급'}<b>${C.won(h2m?monthly:hourly)}</b></div>${low}
  ${C.rows([
    ['주휴시간',hol?`${+hol.toFixed(1)}시간`:'없음 (주 15시간 미만)'],
    ['월 유급시간',`${mh}시간`],
    ['시급',C.won(hourly)],
    ['일급 (8시간)',C.won(hourly*8)],
    ['주급 (주휴 포함)',C.won(hourly*(Math.min(h,40)+hol))],
    ['월급',C.won(monthly)],
    ['연봉 (월급 × 12)',C.won(monthly*12),'sum']])}
  <p class="how">월 유급시간 = (${Math.min(h,40)}시간 + 주휴 ${+hol.toFixed(1)}시간) × 4.345주 ≈ ${mh}시간. 연장근로 수당은 포함하지 않았습니다.</p>`);
});
