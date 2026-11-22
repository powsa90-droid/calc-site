// 고용보험법 제46조·제50조, 2026.1.1 이후 이직자 기준
const MAXD=68100,MINW=10320;
const DAYS={u50:[120,150,180,210,240],o50:[120,180,210,240,270]};
C.onCalc(()=>{
  const w=C.num('wage3'),d3=C.num('d3')||92,h=Math.min(8,C.num('hrs')||8);
  if(w<=0){C.show('res','<p class="msg">퇴직 전 3개월 급여를 입력해 주세요.</p>');return}
  const avg=w/d3;
  const raw=avg*0.6;
  const minD=Math.floor(MINW*0.8*h);
  let daily=Math.floor(Math.min(Math.max(raw,minD),MAXD));
  const note=raw>MAXD?'상한액 적용':raw<minD?'하한액 적용':'평균임금의 60%';
  const n=DAYS[C.radio('age')][+C.$('#ins').value];
  C.show('res',`<div class="big">1일 구직급여<b>${C.won(daily)}</b></div>
  <div class="big" style="margin-top:6px">총 ${n}일 받으면 약 ${C.won(daily*n)}</div>
  ${C.rows([
    ['1일 평균임금',C.won(avg)],
    ['평균임금의 60%',C.won(raw)],
    ['1일 상한액 / 하한액',`${C.fmt(MAXD)}원 / ${C.fmt(minD)}원`],
    ['적용 1일 구직급여',`${C.won(daily)} (${note})`],
    ['한 달(28일) 실업인정 시',C.won(daily*28)],
    ['소정급여일수',`${n}일`],
    ['총 예상 수령액',C.won(daily*n),'sum']])}
  <p class="how">2026년 1월 1일 이후 퇴사자 기준입니다. 하한액은 최저시급 10,320원 × 80% × 1일 소정근로시간입니다. 실제 지급액은 고용센터의 수급자격 심사로 확정됩니다.</p>`);
});
