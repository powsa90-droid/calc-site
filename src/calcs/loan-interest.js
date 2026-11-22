// 대출 상환 스케줄: 원리금균등, 원금균등, 만기일시 (월 이자 = 잔액 × 연이율/12)
function schedule(P,rate,n,g,type){
  const r=rate/100/12,rows=[];let bal=P;
  const m=n-g;
  const pmt=r===0?P/m:P*r*Math.pow(1+r,m)/(Math.pow(1+r,m)-1);
  for(let i=1;i<=n;i++){
    const int=bal*r;let prin=0;
    if(i>g){
      if(type==='epi')prin=pmt-int;
      else if(type==='ep')prin=P/m;
      else prin=i===n?bal:0;
    }
    if(i===n)prin=bal;
    bal-=prin;rows.push([i,prin+int,prin,int,Math.max(0,bal)]);
  }
  return rows;
}
C.onCalc(()=>{
  const P=C.num('amt'),rate=C.num('rate'),n=Math.round(C.num('months')),g=Math.round(C.num('grace')),type=C.radio('type');
  if(P<=0||n<=0){C.show('res','<p class="msg">대출 금액과 기간을 입력해 주세요.</p>');return}
  if(type!=='bullet'&&g>=n){C.show('res','<p class="msg">거치 기간은 대출 기간보다 짧아야 합니다.</p>');return}
  const rows=schedule(P,rate,n,type==='bullet'?0:g,type);
  const totInt=rows.reduce((s,x)=>s+x[3],0);
  const first=rows[Math.min(type==='bullet'?0:g,n-1)];
  const label={epi:'매월 상환액 (원리금균등)',ep:'첫 달 상환액 (원금균등, 매달 줄어듦)',bullet:'매월 이자 (만기에 원금 상환)'}[type];
  const main=type==='bullet'?rows[0][3]:first[1];
  const tbl='<div class="sched"><table><thead><tr><th>회차</th><th>상환액</th><th>원금</th><th>이자</th><th>잔액</th></tr></thead><tbody>'+
    rows.map(x=>`<tr><td>${x[0]}</td><td>${C.fmt(x[1])}</td><td>${C.fmt(x[2])}</td><td>${C.fmt(x[3])}</td><td>${C.fmt(x[4])}</td></tr>`).join('')+'</tbody></table></div>';
  C.show('res',`<div class="big">${label}<b>${C.won(main)}</b></div>
  ${C.rows([
    ['대출 원금',C.won(P)],
    ['총 이자',C.won(totInt)],
    ['총 상환액',C.won(P+totInt),'sum']])}
  ${g>0&&type!=='bullet'?`<p class="how">거치 기간 ${g}개월 동안은 매월 이자 ${C.won(rows[0][3])}만 냅니다.</p>`:''}
  ${tbl}`);
});
