import { useEffect, useMemo, useState } from 'react'
import { LanguageContext } from './language-context'

const translations = {
  'Smarter Soil. Better Harvests.': 'સ્વસ્થ જમીન, વધુ સારો પાક.',
  'The Challenge': 'પડકાર',
  'How It Works': 'આ કેવી રીતે કામ કરે છે',
  'Why Us': 'અમને શા માટે પસંદ કરો',
  'Open Dashboard': 'ડેશબોર્ડ ખોલો',
  'Grow Better.': 'વધુ સારું ઉગાડો.',
  'Farm Smarter.': 'સમજદારીથી ખેતી કરો.',
  'AI-powered soil analysis and personalized fertilizer recommendations for healthier crops, lower costs, and higher yields — because every field is unique.':
    'વધુ સ્વસ્થ પાક, ઓછો ખર્ચ અને વધુ ઉપજ માટે AI આધારિત જમીન વિશ્લેષણ અને વ્યક્તિગત ખાતર ભલામણો — કારણ કે દરેક ખેતર અલગ છે.',
  'Analyze My Soil': 'મારી જમીનનું વિશ્લેષણ કરો',
  'Learn How It Works': 'આ કેવી રીતે કામ કરે છે તે જાણો',
  'Healthy soil is the foundation of every good harvest.': 'સ્વસ્થ જમીન દરેક સારા પાકનો આધાર છે.',
  'Many farmers struggle to determine the right fertilizer for their soil and crops. The wrong choice leads to reduced yields, higher costs, and long-term soil degradation. Guesswork is expensive — and the land pays the price.':
    'ઘણા ખેડૂતોને પોતાની જમીન અને પાક માટે યોગ્ય ખાતર પસંદ કરવામાં મુશ્કેલી પડે છે. ખોટી પસંદગીથી ઉપજ ઘટે છે, ખર્ચ વધે છે અને જમીનને લાંબા ગાળે નુકસાન થાય છે. અંદાજે કરેલી ખેતી મોંઘી પડે છે — અને જમીનને તેની કિંમત ચૂકવવી પડે છે.',
  'Neer Niti replaces guesswork with data. We analyze your soil nutrients, crop needs, and local conditions to recommend precisely what your field requires — no more, no less.':
    'નીર નીતિ અંદાજના બદલે માહિતીનો ઉપયોગ કરે છે. અમે જમીનનાં પોષક તત્ત્વો, પાકની જરૂરિયાતો અને સ્થાનિક પરિસ્થિતિઓનું વિશ્લેષણ કરીને ખેતરને જેટલા ખાતરની જરૂર હોય એટલી જ ભલામણ કરીએ છીએ.',
  'Learn More': 'વધુ જાણો',
  'Enter your soil and crop details': 'જમીન અને પાકની વિગતો દાખલ કરો',
  'Provide information about your soil, crop, growth stage, and farming conditions. Partial data is fine — we work with what you have.':
    'જમીન, પાક, વૃદ્ધિના તબક્કા અને ખેતીની પરિસ્થિતિઓ વિશે માહિતી આપો. બધી માહિતી ન હોય તો પણ ચાલશે — ઉપલબ્ધ માહિતીથી કામ થશે.',
  'Our AI analyzes the data': 'અમારું AI માહિતીનું વિશ્લેષણ કરે છે',
  'We use a machine-learning model trained on real agricultural data, combined with agronomic nutrient references.':
    'અમે વાસ્તવિક કૃષિ માહિતીથી તાલીમ પામેલા મશીન-લર્નિંગ મોડેલ અને કૃષિ પોષક તત્ત્વોના સંદર્ભોનો ઉપયોગ કરીએ છીએ.',
  'Get a personalized recommendation': 'તમારા માટે ખાસ ભલામણ મેળવો',
  'Receive a cost-optimized fertilizer plan tailored to your specific soil and crop requirements.':
    'તમારી જમીન અને પાકની જરૂરિયાત મુજબ ખર્ચને ધ્યાનમાં રાખીને તૈયાર કરેલી ખાતર યોજના મેળવો.',
  'Improve your yields': 'તમારી ઉપજ વધારો',
  'Make informed decisions, reduce waste, and grow healthier, more productive crops season after season.':
    'માહિતી આધારિત નિર્ણયો લો, બગાડ ઘટાડો અને દરેક ઋતુમાં વધુ સ્વસ્થ તથા વધુ ઉપજ આપતા પાક ઉગાડો.',
  'From soil sample to smart decision in four steps.': 'જમીનના નમૂનાથી સમજદારીભર્યા નિર્ણય સુધી — ચાર પગલાંમાં.',
  'Data-driven soil analysis': 'માહિતી આધારિત જમીન વિશ્લેષણ',
  'Aggregates multiple soil readings per farm with proper statistics and flags out-of-range values.':
    'દરેક ખેતરનાં અનેક જમીન માપનોનું આંકડાકીય સરવૈયું કરે છે અને સામાન્ય મર્યાદાની બહારનાં મૂલ્યો દર્શાવે છે.',
  'Cost-optimized recommendations': 'ખર્ચને અનુરૂપ ભલામણો',
  'A linear-programming solver finds the lowest-cost fertilizer mix that meets your crop nutrient targets.':
    'લીનિયર-પ્રોગ્રામિંગ પદ્ધતિ પાકની પોષક જરૂરિયાતો પૂરી કરતું સૌથી ઓછા ખર્ચનું ખાતર મિશ્રણ શોધે છે.',
  'Honest and transparent': 'પ્રામાણિક અને પારદર્શક',
  'Every recommendation shows its assumptions, price sources, and any unmet requirements — no black boxes.':
    'દરેક ભલામણમાં ધારણાઓ, ભાવના સ્રોતો અને બાકી રહેલી જરૂરિયાતો સ્પષ્ટ દર્શાવાય છે — કોઈ છુપાવેલી પ્રક્રિયા નહીં.',
  'Better decisions, healthier crops.': 'વધુ સારા નિર્ણયો, વધુ સ્વસ્થ પાક.',
  'Why Choose Us': 'અમને શા માટે પસંદ કરો',
  'Soil & Nutrients': 'જમીન અને પોષક તત્ત્વો',
  'Neer Niti analyzes your soil nutrients, crop needs, and environmental conditions to recommend the right fertilizer — because every field is unique.':
    'દરેક ખેતર અલગ હોવાથી, નીર નીતિ યોગ્ય ખાતર સૂચવવા માટે જમીનનાં પોષક તત્ત્વો, પાકની જરૂરિયાતો અને પર્યાવરણીય પરિસ્થિતિઓનું વિશ્લેષણ કરે છે.',
  'Higher Productivity': 'વધુ ઉત્પાદન',
  'Healthier Soil': 'વધુ સ્વસ્થ જમીન',
  'Lower Costs': 'ઓછો ખર્ચ',
  'Sustainable Farming': 'ટકાઉ ખેતી',
  'Understanding what your soil truly needs.': 'તમારી જમીનને ખરેખર શેની જરૂર છે તે જાણો.',
  "Balanced nutrition is the difference between a surviving crop and a thriving one. We account for the three core nutrients and your soil's pH together.":
    'સંતુલિત પોષણથી પાક માત્ર ટકી રહેવાને બદલે સારી રીતે વિકસે છે. અમે ત્રણ મુખ્ય પોષક તત્ત્વો અને જમીનના pH બંનેને ધ્યાનમાં લઈએ છીએ.',
  'Nitrogen (N)': 'નાઇટ્રોજન (N)',
  'Drives leafy, vegetative growth and vivid green color.': 'પાંદડાંની વૃદ્ધિ અને ઘેરા લીલા રંગમાં મદદ કરે છે.',
  'Phosphorus (P₂O₅)': 'ફોસ્ફરસ (P₂O₅)',
  'Builds strong roots and supports flowering and fruiting.': 'મજબૂત મૂળ બનાવે છે અને ફૂલ તથા ફળ આવવામાં મદદ કરે છે.',
  'Potassium (K₂O)': 'પોટેશિયમ (K₂O)',
  'Improves resilience, water regulation, and crop quality.': 'પ્રતિકારશક્તિ, પાણીનું નિયમન અને પાકની ગુણવત્તા સુધારે છે.',
  'Ready when you are': 'તમે તૈયાર હો ત્યારે',
  'Technology that understands your land.': 'તમારી જમીનને સમજતી ટેક્નોલોજી.',
  'Start with a single soil analysis and see exactly what your field needs — and what it will cost.':
    'એક જમીન વિશ્લેષણથી શરૂઆત કરો અને તમારા ખેતરને શું જોઈએ છે તથા તેનો કેટલો ખર્ચ થશે તે જાણો.',
  'Start Analyzing': 'વિશ્લેષણ શરૂ કરો',
  'Healthy soil builds a better tomorrow.': 'સ્વસ્થ જમીનથી આવતીકાલ વધુ સારી બને છે.',
  Platform: 'પ્લેટફોર્મ',
  Dashboard: 'ડેશબોર્ડ',
  History: 'ઇતિહાસ',
  Learn: 'જાણો',
  'All rights reserved.': 'બધા હકો સુરક્ષિત.',
  'Recommendations are advisory. Consult a certified agronomist for field-specific decisions.':
    'ભલામણો માર્ગદર્શન માટે છે. તમારા ખેતર માટેના નિર્ણયોમાં પ્રમાણિત કૃષિ નિષ્ણાતની સલાહ લો.',
  Home: 'મુખ્ય પૃષ્ઠ',
  'Analyze Soil': 'જમીનનું વિશ્લેષણ',
  Profile: 'પ્રોફાઇલ',
  'Open menu': 'મેનુ ખોલો',
  'Close menu': 'મેનુ બંધ કરો',
  'Main navigation': 'મુખ્ય નેવિગેશન',
  'Good Morning': 'સુપ્રભાત',
  'Good Afternoon': 'નમસ્કાર',
  'Good Evening': 'શુભ સાંજ',
  Farmer: 'ખેડૂત',
  'Notifications': 'સૂચનાઓ',
  "Let's make your farm more productive with the right fertilizer.":
    'યોગ્ય ખાતરથી તમારા ખેતરને વધુ ઉત્પાદક બનાવીએ.',
  'Welcome back, {name}': 'ફરી સ્વાગત છે, {name}',
  'Welcome to NeerNiti': 'નીર નીતિમાં સ્વાગત છે',
  "Let's make your field more productive.": 'તમારા ખેતરને વધુ ઉત્પાદક બનાવીએ.',
  'Record your soil readings and get a cost-optimized fertilizer recommendation tailored to your crop.':
    'જમીનનાં માપનો નોંધો અને તમારા પાકને અનુરૂપ ખર્ચ-અનુકૂળ ખાતર ભલામણ મેળવો.',
  'Start by adding your farm': 'તમારું ખેતર ઉમેરીને શરૂઆત કરો',
  'Create your first farm to record soil readings and generate recommendations. It only takes a moment.':
    'જમીનનાં માપનો નોંધવા અને ભલામણો મેળવવા માટે તમારું પહેલું ખેતર ઉમેરો. તેમાં થોડો જ સમય લાગશે.',
  'Add a farm & analyze': 'ખેતર ઉમેરો અને વિશ્લેષણ કરો',
  'Active farm': 'સક્રિય ખેતર',
  'Soil & nutrient overview': 'જમીન અને પોષક તત્ત્વોની ઝાંખી',
  'Add reading': 'માપન ઉમેરો',
  "Couldn't load soil data": 'જમીનનો ડેટા લાવી શકાયો નહીં',
  'Quick actions': 'ઝડપી વિકલ્પો',
  'View History': 'ઇતિહાસ જુઓ',
  'Farm Profile': 'ખેતરની પ્રોફાઇલ',
  'Recent recommendations': 'તાજેતરની ભલામણો',
  'View all': 'બધું જુઓ',
  "Couldn't load recommendations": 'ભલામણો લાવી શકાયી નહીં',
  'No recommendations yet': 'હજુ કોઈ ભલામણ નથી',
  'Run your first soil analysis to see personalized fertilizer recommendations here.':
    'વ્યક્તિગત ખાતર ભલામણો અહીં જોવા માટે પ્રથમ જમીન વિશ્લેષણ કરો.',
  "Couldn't load your farms": 'તમારા ખેતરો લાવી શકાયા નહીં',
  'No numeric soil measurements have been recorded yet. Add a soil reading to see aggregated statistics.':
    'હજુ સુધી જમીનનાં આંકડાકીય માપનો નોંધાયા નથી. સરવાળાના આંકડા જોવા માટે જમીનનું માપન ઉમેરો.',
  'Soil pH': 'જમીનનો pH',
  'Electrical Conductivity': 'વિદ્યુત વાહકતા',
  Moisture: 'ભેજ',
  'Phosphorus (P)': 'ફોસ્ફરસ (P)',
  'Potassium (K)': 'પોટેશિયમ (K)',
  'Organic Carbon': 'જૈવિક કાર્બન',
  'from 1 reading': '1 માપનમાંથી',
  'avg of {count} readings · {min}–{max}': '{count} માપનોની સરેરાશ · {min}–{max}',
  Recommendation: 'ભલામણ',
  ' est. total': ' અંદાજિત કુલ',
  Progress: 'પ્રગતિ',
  'Generate a fertilizer recommendation': 'ખાતરની ભલામણ મેળવો',
  'Three quick steps: choose your farm, enter any soil measurements you have, and pick your crop.':
    'ત્રણ સરળ પગલાં: ખેતર પસંદ કરો, ઉપલબ્ધ જમીનનાં માપનો દાખલ કરો અને પાક પસંદ કરો.',
  Farm: 'ખેતર',
  Soil: 'જમીન',
  'Crop & Options': 'પાક અને વિકલ્પો',
  Back: 'પાછળ',
  Continue: 'આગળ વધો',
  'Generating…': 'બનાવી રહ્યા છીએ…',
  'Get Recommendation': 'ભલામણ મેળવો',
  'Which farm are we analyzing?': 'કયા ખેતરનું વિશ્લેષણ કરવું છે?',
  'Pick an existing farm or add a new one. Coordinates are optional but let us fetch local weather for your analysis.':
    'હાલનું ખેતર પસંદ કરો અથવા નવું ઉમેરો. સ્થાનાંક વૈકલ્પિક છે, પરંતુ તે સ્થાનિક હવામાનની માહિતી મેળવવામાં મદદ કરે છે.',
  'Use an existing farm': 'હાલનું ખેતર વાપરો',
  'Add a new farm': 'નવું ખેતર ઉમેરો',
  'Select farm': 'ખેતર પસંદ કરો',
  'Farm name': 'ખેતરનું નામ',
  'e.g. Green Valley Farm': 'દા.ત. હરિયાળું ખેતર',
  Area: 'વિસ્તાર',
  'Optional. Used to scale total fertilizer quantities.': 'વૈકલ્પિક. ખાતરની કુલ માત્રા ગણવા ઉપયોગી.',
  'Area unit': 'વિસ્તારનો એકમ',
  Latitude: 'અક્ષાંશ',
  'Optional — provide with longitude for weather.': 'વૈકલ્પિક — હવામાન માટે રેખાંશ સાથે દાખલ કરો.',
  Longitude: 'રેખાંશ',
  'Location description': 'સ્થાનની વિગતો',
  'Optional.': 'વૈકલ્પિક.',
  'e.g. Village Rampur, District Agra': 'દા.ત. ગામ રામપુર, જિલ્લો આગ્રા',
  'Enter your soil measurements': 'જમીનનાં માપનો દાખલ કરો',
  'Add whatever you have — a lab report or sensor reading. Every field is optional, but please include the unit for any value you enter.':
    'તમારી પાસે જે હોય તે દાખલ કરો — લેબ રિપોર્ટ કે સેન્સરનું માપન. દરેક માહિતી વૈકલ્પિક છે, પરંતુ દાખલ કરેલા મૂલ્યનો એકમ જરૂર પસંદ કરો.',
  'Soil properties': 'જમીનના ગુણધર્મો',
  '0–14. Typical agronomic range is 4.0–8.5.': '0–14. સામાન્ય કૃષિ મર્યાદા 4.0–8.5 છે.',
  Unit: 'એકમ',
  'Electrical conductivity': 'વિદ્યુત વાહકતા',
  'Organic carbon': 'જૈવિક કાર્બન',
  'Nutrients (N–P–K)': 'પોષક તત્ત્વો (N–P–K)',
  'Nitrogen, phosphorus, and potassium must share a single unit.':
    'નાઇટ્રોજન, ફોસ્ફરસ અને પોટેશિયમ માટે એક જ એકમ વાપરો.',
  Nitrogen: 'નાઇટ્રોજન',
  Phosphorus: 'ફોસ્ફરસ',
  Potassium: 'પોટેશિયમ',
  'N–P–K unit': 'N–P–K એકમ',
  "Temperature, humidity, and rainfall are fetched automatically from a weather service using your farm's coordinates — you don't need to enter them here.":
    'તાપમાન, ભેજ અને વરસાદની માહિતી તમારા ખેતરના સ્થાનાંક પરથી આપમેળે મેળવવામાં આવશે — અહીં દાખલ કરવાની જરૂર નથી.',
  'Tell us about your crop': 'તમારા પાક વિશે જણાવો',
  'The recommendation is tailored to your crop and its current growth stage.':
    'ભલામણ તમારા પાક અને તેના હાલના વૃદ્ધિ તબક્કા મુજબ તૈયાર થશે.',
  Crop: 'પાક',
  'Loading crops…': 'પાકની માહિતી લાવી રહ્યા છીએ…',
  'Select a crop': 'પાક પસંદ કરો',
  'Growth stage': 'વૃદ્ધિનો તબક્કો',
  'Select a stage': 'તબક્કો પસંદ કરો',
  'Cultivated area': 'વાવેતર વિસ્તાર',
  "Optional. In hectares. Defaults to the farm's area if left blank.":
    'વૈકલ્પિક. હેક્ટરમાં. ખાલી રાખો તો ખેતરનો વિસ્તાર લેવામાં આવશે.',
  Options: 'વિકલ્પો',
  'Use local weather': 'સ્થાનિક હવામાન વાપરો',
  "Fetch current conditions from your farm's coordinates. Skipped automatically if the farm has no coordinates.":
    'ખેતરના સ્થાનાંક પરથી હાલની હવામાન પરિસ્થિતિ મેળવો. સ્થાનાંક ન હોય તો આ પગલું આપમેળે છોડી દેવાશે.',
  'Allow illustrative / unverified prices': 'ઉદાહરણરૂપ / ચકાસ્યા વિનાના ભાવ માન્ય રાખો',
  'The catalogue currently ships sample prices only. Enable this to get a cost-optimized plan — results will clearly mark prices as unverified.':
    'હાલની યાદીમાં માત્ર નમૂનાના ભાવ છે. ઓછા ખર્ચની યોજના મેળવવા આ વિકલ્પ ચાલુ કરો — પરિણામમાં ભાવ ચકાસેલા નથી તે સ્પષ્ટ દર્શાવાશે.',
  'Recommendation generated.': 'ખાતરની ભલામણ તૈયાર થઈ.',
  'Something went wrong. Please try again.': 'કંઈક ખોટું થયું. કૃપા કરીને ફરી પ્રયાસ કરો.',
  'Could not load the crop list.': 'પાકની યાદી લાવી શકાયી નહીં.',
  'Please enter a farm name.': 'ખેતરનું નામ દાખલ કરો.',
  'Area must be greater than 0.': 'વિસ્તાર 0 કરતાં વધુ હોવો જોઈએ.',
  'Provide latitude and longitude together, or neither.': 'અક્ષાંશ અને રેખાંશ બંને દાખલ કરો અથવા બંને ખાલી રાખો.',
  'Latitude must be between -90 and 90.': 'અક્ષાંશ -90 થી 90 વચ્ચે હોવો જોઈએ.',
  'Longitude must be between -180 and 180.': 'રેખાંશ -180 થી 180 વચ્ચે હોવો જોઈએ.',
  'Please select a farm.': 'ખેતર પસંદ કરો.',
  'Select a moisture unit.': 'ભેજનો એકમ પસંદ કરો.',
  'Select an EC unit.': 'ECનો એકમ પસંદ કરો.',
  'Select an organic carbon unit.': 'જૈવિક કાર્બનનો એકમ પસંદ કરો.',
  'Select an N–P–K unit.': 'N–P–Kનો એકમ પસંદ કરો.',
  'Please select a crop.': 'પાક પસંદ કરો.',
  'Please select a growth stage.': 'વૃદ્ધિનો તબક્કો પસંદ કરો.',
  'Your recommendation history': 'તમારી ભલામણોનો ઇતિહાસ',
  'Past soil analyses and fertilizer recommendations.': 'અગાઉનાં જમીન વિશ્લેષણ અને ખાતરની ભલામણો.',
  'No farms yet': 'હજુ કોઈ ખેતર ઉમેર્યું નથી',
  'Add your first farm and run a soil analysis to start building your history.':
    'ઇતિહાસ શરૂ કરવા તમારું પહેલું ખેતર ઉમેરો અને જમીનનું વિશ્લેષણ કરો.',
  'Search by fertilizer (e.g. Urea)': 'ખાતરથી શોધો (દા.ત. યુરિયા)',
  'Search recommendations': 'ભલામણો શોધો',
  'Filter by status': 'સ્થિતિ પ્રમાણે ગાળો',
  'All statuses': 'બધી સ્થિતિઓ',
  'Plan ready': 'યોજના તૈયાર',
  'No feasible plan': 'યોગ્ય યોજના ઉપલબ્ધ નથી',
  'Needs crop data': 'પાકની માહિતી જરૂરી',
  'Needs prices': 'ભાવની માહિતી જરૂરી',
  "Couldn't load history": 'ઇતિહાસ લાવી શકાયો નહીં',
  'Once you run a soil analysis, your recommendations will appear here for easy reference.':
    'જમીનનું વિશ્લેષણ કર્યા પછી તમારી ભલામણો અહીં સરળ સંદર્ભ માટે દેખાશે.',
  'Run your first analysis': 'પ્રથમ વિશ્લેષણ કરો',
  'No matches': 'કોઈ મેળ મળ્યો નથી',
  'No recommendations match your search or filter. Try adjusting them.':
    'તમારી શોધ અથવા ગાળણ સાથે કોઈ ભલામણ મેળ ખાતી નથી. તેમાં ફેરફાર કરીને જુઓ.',
  'Showing {shown} of {total} recommendations': '{total}માંથી {shown} ભલામણો બતાવી રહ્યા છીએ',
  'Your profile & farm': 'તમારી પ્રોફાઇલ અને ખેતર',
  'Manage your display name and the details of your selected farm.':
    'તમારું દર્શાવવાનું નામ અને પસંદ કરેલા ખેતરની વિગતો સંભાળો.',
  'This app currently runs without server-side accounts. Your name and selected farm are stored only on this device. Farm records themselves are saved on the server.':
    'હાલ આ એપ સર્વર પરના વ્યક્તિગત ખાતા વિના ચાલે છે. તમારું નામ અને પસંદ કરેલું ખેતર ફક્ત આ ઉપકરણ પર સંગ્રહાય છે. ખેતરની વિગતો સર્વર પર સાચવાય છે.',
  'Farmer details': 'ખેડૂતની વિગતો',
  'Display name': 'દર્શાવવાનું નામ',
  'Used to greet you across the app.': 'એપમાં તમને સંબોધવા માટે વપરાય છે.',
  'e.g. Ramesh Kumar': 'દા.ત. રમેશભાઈ પટેલ',
  'Saving…': 'સાચવી રહ્યા છીએ…',
  'Save name': 'નામ સાચવો',
  'Farm details': 'ખેતરની વિગતો',
  'Loading your farm…': 'તમારા ખેતરની માહિતી લાવી રહ્યા છીએ…',
  'No farm yet': 'હજુ ખેતર નથી',
  'Add your first farm through the soil analysis flow.':
    'જમીન વિશ્લેષણની પ્રક્રિયા દ્વારા તમારું પહેલું ખેતર ઉમેરો.',
  'Your name has been saved.': 'તમારું નામ સાચવાયું છે.',
  'Farm details updated.': 'ખેતરની વિગતો અપડેટ થઈ.',
  'Could not update the farm.': 'ખેતરની વિગતો અપડેટ થઈ શકી નહીં.',
  'Signed out on this device.': 'આ ઉપકરણમાંથી સાઇન આઉટ થયા.',
  'Farm name is required.': 'ખેતરનું નામ જરૂરી છે.',
  'pH must be between 0 and 14.': 'pH 0 થી 14 વચ્ચે હોવો જોઈએ.',
  '{field} must be a number.': '{field} આંકડો હોવો જોઈએ.',
  '{field} must be between {min} and {max}.': '{field} {min} અને {max}ની વચ્ચે હોવું જોઈએ.',
  'Farm "{name}" created.': 'ખેતર "{name}" બનાવાયું.',
  'Past soil analyses and recommendations for {farm}.': '{farm} માટેનાં અગાઉનાં જમીન વિશ્લેષણ અને ભલામણો.',
  'Sowing': 'વાવણી',
  'Germination': 'અંકુરણ',
  'Vegetative': 'વૃદ્ધિ',
  'Flowering': 'ફૂલ આવવાનો તબક્કો',
  'Maturity': 'પરિપક્વતા',
  'Harvest': 'લણણી',
  Rice: 'ચોખા',
  Wheat: 'ઘઉં',
  Maize: 'મકાઈ',
  Cotton: 'કપાસ',
  Potato: 'બટાકા',
  Sugarcane: 'શેરડી',
  Tomato: 'ટામેટાં',
  Soybean: 'સોયાબીન',
  Groundnut: 'મગફળી',
  Mustard: 'રાઈ',
  Urea: 'યુરિયા',
  'DAP (Di-ammonium Phosphate)': 'ડીએપી (ડાય-એમોનિયમ ફોસ્ફેટ)',
  'MOP (Muriate of Potash)': 'એમઓપી (મ્યુરિએટ ઓફ પોટાશ)',
  'NPK 10-26-26': 'NPK 10-26-26',
  'NPK 12-32-16': 'NPK 12-32-16',
  'SSP (Single Super Phosphate)': 'એસએસપી (સિંગલ સુપર ફોસ્ફેટ)',
  'Zinc Sulphate (ZnSO₄ 33%)': 'ઝિંક સલ્ફેટ (ZnSO₄ 33%)',
  'Compost (Farm Yard Manure)': 'ખાતર (છાણિયું ખાતર)',
  "Couldn't load this recommendation": 'આ ભલામણ લાવી શકાયી નહીં',
  'Back to history': 'ઇતિહાસ પર પાછા જાઓ',
  'Suggested fertilizer category': 'સૂચવેલ ખાતરનો પ્રકાર',
  'Model probability for this class:': 'આ વર્ગ માટે મોડેલની સંભાવના:',
  'Not available': 'ઉપલબ્ધ નથી',
  'The ML category suggestion could not be produced for this request.':
    'આ વિનંતી માટે ML વર્ગનું સૂચન તૈયાર થઈ શક્યું નથી.',
  "Model's top candidates": 'મોડેલના મુખ્ય વિકલ્પો',
  "These are the classifier's raw probabilities — a statistical signal, not a calibrated certainty.":
    'આ વર્ગીકરણ મોડેલની મૂળ સંભાવનાઓ છે — આ આંકડાકીય સંકેત છે, નિશ્ચિત આગાહી નથી.',
  'Cost-optimized plan': 'ઓછા ખર્ચની યોજના',
  'A cost-optimized fertilizer plan was found.': 'ઓછા ખર્ચની ખાતર યોજના મળી.',
  'No available fertilizer combination could meet the nutrient targets.':
    'પોષક તત્ત્વોની જરૂરિયાત પૂરી કરી શકે એવું ખાતર મિશ્રણ ઉપલબ્ધ નથી.',
  'This crop/stage is not in the nutrient reference table, so optimization was skipped.':
    'પોષક તત્ત્વોના સંદર્ભ કોષ્ટકમાં આ પાક અથવા તબક્કો નથી, તેથી ગણતરી કરવામાં આવી નથી.',
  'No usable fertilizer prices were available for optimization.':
    'ગણતરી માટે ખાતરના ઉપયોગી ભાવ ઉપલબ્ધ નહોતા.',
  'Pending': 'બાકી',
  'Not yet computed.': 'હજુ ગણતરી થઈ નથી.',
  'Error': 'ભૂલ',
  'An error occurred during optimization.': 'ગણતરી દરમિયાન ભૂલ થઈ.',
  'Estimated total cost': 'અંદાજિત કુલ ખર્ચ',
  'Illustrative price': 'ઉદાહરણરૂપ ભાવ',
  'Unverified price': 'ચકાસ્યા વિનાનો ભાવ',
  Quantity: 'જથ્થો',
  'Unit price': 'એકમનો ભાવ',
  'Line cost': 'કુલ કિંમત',
  'Price source:': 'ભાવનો સ્રોત:',
  recorded: 'નોંધાયેલ',
  'No fertilizer plan was produced for this recommendation. See the notes below for why, and what to adjust.':
    'આ ભલામણ માટે ખાતરની યોજના બની નથી. કારણ અને જરૂરી ફેરફારો માટે નીચેની નોંધો જુઓ.',
  'Nutrient requirements': 'પોષક તત્ત્વોની જરૂરિયાત',
  Required: 'જરૂરી',
  Supplied: 'પૂરા પાડેલા',
  'Short by {amount} kg/ha': '{amount} kg/haની ઘટ',
  Warnings: 'ચેતવણીઓ',
  Assumptions: 'ધારણાઓ',
  'Run another analysis': 'બીજું વિશ્લેષણ કરો',
  'View all recommendations': 'બધી ભલામણો જુઓ',
  'Loading': 'લાવી રહ્યા છીએ',
}

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    try {
      return localStorage.getItem('neerniti-language') === 'gu' ? 'gu' : 'en'
    } catch {
      return 'en'
    }
  })

  useEffect(() => {
    document.documentElement.lang = language
    try {
      localStorage.setItem('neerniti-language', language)
    } catch {
      // The selected language still works for the current page if storage is unavailable.
    }
  }, [language])

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t: (text, values = {}) => {
        const translated = language === 'gu' ? translations[text] || text : text
        return translated.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? `{${key}}`)
      },
    }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}
