'use strict';
// Only confirmed lead creations count as a lead conversion.
// No PII, phone/email, lead-reference or payments are sent to Google.
(()=>{
 const seen=new Set();
 const allowedMethods=new Set(['english_contact_form','hi_contact_form','hinglish_contact_form','homepage_free_audit','build_form']);
 window.FreshtiqLeadConversion={
   confirmed({lead_ref,method,country='India',service='general',updated}={}){
     const ref=String(lead_ref||'').trim();
     // The backend returns updated:true for a revised existing lead; it must
     // NOT be counted as another new enquiry in Ads/GA4.
     if(updated!==false||!ref||ref.length>100||!allowedMethods.has(method)||country!=='India')return false;
     if(seen.has(ref))return false;
     seen.add(ref);
     try{
       if(localStorage.getItem('ftq_analytics_consent_v1')!=='granted')return false;
       if(typeof window.gtag!=='function')return false;
       const type=service==='whatsapp_ai_sales_bot'?'whatsapp_ai_sales_bot':'general';
       window.gtag('event','generate_lead',{
         method,lead_source:'website_confirmed_form',country:'India',service:type
       });
       return true;
     }catch(_){return false}
   }
 };
})();
