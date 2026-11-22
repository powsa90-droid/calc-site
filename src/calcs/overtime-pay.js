// 근로기준법 제56조: 연장 50%, 야간 50%, 휴일 8시간 이내 50%·초과 100% 가산 (5인 미만 미적용)
C.onCalc(()=>{
  const w=C.num('wage'),ot=C.num('ot'),ni=C.num('night'),h8=C.num('hol8'),hx=C.num('holx');
  if(w<=0){C.show('res','<p class="msg">통상시급을 입력해 주세요.</p>');return}
  const big=C.radio('size')==='5';
  const k=big?1:0;
  const a=w*ot*(1+0.5*k),b=w*h8*(1+0.5*k),c=w*hx*(1+1*k),n=w*ni*0.5*k;
  const tot=a+b+c+n;
  C.show('res',`<div class="big">수당 합계<b>${C.won(tot)}</b></div>
  ${big?'':'<p class="msg">5인 미만 사업장은 연장·야간·휴일 가산수당 규정이 적용되지 않아 일한 시간만큼의 통상임금만 계산했습니다.</p>'}
  ${C.rows([
    [`연장근로 ${ot}시간 (×${big?1.5:1})`,C.won(a)],
    [`휴일근로 8시간 이내 ${h8}시간 (×${big?1.5:1})`,C.won(b)],
    [`휴일근로 8시간 초과 ${hx}시간 (×${big?2:1})`,C.won(c)],
    [`야간근로 가산 ${ni}시간 (×0.5 추가)`,C.won(n)],
    ['합계',C.won(tot),'sum']])}
  <p class="how">야간근로는 다른 근로 시간과 겹쳐도 가산분 50%를 따로 더합니다. 예를 들어 밤 11시에 한 연장근로는 1.5배에 0.5배가 더해져 통상시급의 2배가 됩니다. 야간 시간이 소정근로시간 안이라면 그 시간의 기본 임금은 월급에 이미 들어 있어 가산분만 계산했습니다.</p>`);
});
