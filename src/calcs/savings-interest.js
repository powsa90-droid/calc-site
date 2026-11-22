// 예금·적금 만기 이자 (단리·월복리), 이자소득세 15.4% / 세금우대 9.5% / 비과세
document.querySelectorAll('input[name="kind"]').forEach(el=>el.addEventListener('change',()=>{
  C.$('#amtLabel').textContent=C.radio('kind')==='sav'?'월 납입액':'예치 금액';
}));
C.onCalc(()=>{
  const A=C.num('amt'),rate=C.num('rate')/100,n=Math.round(C.num('months')),kind=C.radio('kind'),comp=C.radio('comp'),tv=C.radio('tax'),tax=(tv==='custom'?C.num('taxc'):parseFloat(tv))/100;
  if(A<=0||n<=0){C.show('res','<p class="msg">금액과 기간을 입력해 주세요.</p>');return}
  const r=rate/12;let principal,interest;
  if(kind==='sav'){
    principal=A*n;
    if(comp==='simple')interest=A*r*n*(n+1)/2;
    else{interest=0;for(let k=1;k<=n;k++)interest+=A*(Math.pow(1+r,k)-1)}
  }else{
    principal=A;
    interest=comp==='simple'?A*rate*n/12:A*(Math.pow(1+r,n)-1);
  }
  interest=Math.floor(interest);
  const t=Math.floor(interest*tax/10)*10;
  const after=principal+interest-t;
  C.show('res',`<div class="big">세후 만기 수령액<b>${C.won(after)}</b></div>
  ${C.rows([
    ['원금 합계',C.won(principal)],
    ['세전 이자',C.won(interest)],
    [`이자 과세 (${(tax*100).toFixed(1)}%)`,'-'+C.won(t),'minus'],
    ['세후 이자',C.won(interest-t)],
    ['세후 만기 수령액',C.won(after),'sum']])}
  ${kind==='sav'?`<p class="how">적금은 매달 넣은 돈마다 남은 기간만큼만 이자가 붙습니다. 그래서 연 ${(rate*100).toFixed(2)}% 적금의 실제 수익률은 원금 전체 기준으로 약 ${(interest/principal*100).toFixed(2)}%입니다.</p>`:''}`);
});
