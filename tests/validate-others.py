"""
evaluate manifests from other organisations against the MPEG DASH schema

developed by Paul Higgs using Python 3.9.1
uses the following libraries
 * requests,    python -m pip install requests
 * lxml,        python -m pip install lxml

"""

import sys
import unittest
import logging
import glob
import requests
import json

from lxml import etree

# mpd URLs taken from https://dvb-2017-dm.s3.eu-central-1.amazonaws.com/overview.html 
DVBManifests = [
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/0.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/1.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/2.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/3.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/4.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/5.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/6.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/7.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/8.mpd", 
 "https://a09ac5ffb43c4015b4a006d2b85fa289.mediatailor.eu-central-1.amazonaws.com/v1/dash/6531e8093d869efd0cb1a0354ebd2f3411a4bb88/testmp/.mpd", 
 "https://ylxa8rnu79.execute-api.eu-central-1.amazonaws.com/learning.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/1.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/3.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/5.mpd",
 "https://pl8q5ug7b6.execute-api.eu-central-1.amazonaws.com/6.mpd",
 "https://demo.unified-streaming.com/video/tears-of-steel/tears-of-steel-dash-widevine-playready.ism/.mpd",
 "https://demo.unified-streaming.com/video/tears-of-steel/tears-of-steel-dash-widevine-playready.ism/.mpd",
 "https://livesim.dashif.org/livesim-chunked/chunkdur_1/ato_7/testpic4_8s/Manifest.mpd",
 "https://testlowlat.harmonicinc.com/Content/DASH/Live/channel(dash_ll_time)/manifest.mpd",
 "https://pf5.broadpeak-vcdn.com/bpk-tv/tvrll/llcmaf/index.mpd",
 "https://akamaibroadcasteruseast.akamaized.net/cmaf/live/657078/akasource/out.mpd",
 "https://live.unified-streaming.com/scte35/scte35.isml/.mpd",
 "https://d3tsbu4e72p918.cloudfront.net/dolbyac4/manifest.mpd",
 "https://dvb-2017-dm.s3.eu-central-1.amazonaws.com/ST2094-10.mpd",
 "https://dvb-2017-dm.s3.eu-central-1.amazonaws.com/SL-HDR2.mpd",
 "https://dvb-2017-dm.s3.eu-central-1.amazonaws.com/SL-HDR2-on-off.mpd",
 "https://dvb-2017-dm.s3.eu-central-1.amazonaws.com/ST2094-10-on-off.mpd"
]

# mpd URLs taken from http://refapp.hbbtv.org/videos/
HbbTVManifests=[
 # Caminandes 01, Llama Drama (25fps, 75gop, 1080p, KID=1234) v3
 "http://refapp.hbbtv.org/videos/01_llama_drama_1080p_25f75g6sv3/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_1080p_25f75g6sv3/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_1080p_25f75g6sv3/drm/manifest_clearkey.mpd",
 # Caminandes 02, Gran Dillama (25fps, 75gop, 1080p, KID=1236) v5
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest_subib_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/manifest_subob_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_subib_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_subob_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_playready.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_marlin.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_widevine.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f75g6sv5/drm/manifest_clearkey.mpd",
 # Tears of Steel (25fps, 75gop, 1080p, KID=1237) v3
 "http://refapp.hbbtv.org/videos/tears_of_steel_1080p_25f75g6sv3/manifest.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_1080p_25f75g6sv3/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_1080p_25f75g6sv3/drm/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_1080p_25f75g6sv3/drm/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_1080p_25f75g6sv3/drm/manifest_clearkey.mpd",
 # Caminandes 02, Gran Dillama (25fps, 75gop, 1080p, KID=1236), multiaudio v4
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest_subib_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/manifest_subob_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_subib_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_subob_evtib.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv4/drm/manifest_clearkey.mpd",
 # Caminandes 02, Gran Dillama (25fps, 75gop, 1080p, KID=1236), multiaudio v5
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv5/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_ma_25f75g6sv5/drm/manifest.mpd",
 # Caminandes 01, Llama Drama (25fps, 75gop, 2160p h265, KID=1235) v3
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160p_25f75g6sv3/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160p_25f75g6sv3/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160p_25f75g6sv3/drm/manifest_clearkey.mpd",
 # Caminandes 01, Llama Drama (25fps, 75gop, 1080p h265, KID=1235) v2
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160pmr_25f75g6sv2/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160pmr_25f75g6sv2/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/01_llama_drama_2160pmr_25f75g6sv2/drm/manifest_clearkey.mpd",
 # Caminandes 03, Llamigos (25fps, 75gop, 2160p h265, KID=1238) v2
 "http://refapp.hbbtv.org/videos/03_llamigos_2160psr_25f75g6sv2/manifest.mpd",
 "http://refapp.hbbtv.org/videos/03_llamigos_2160psr_25f75g6sv2/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/03_llamigos_2160psr_25f75g6sv2/drm/manifest_clearkey.mpd",
 # Tears of Steel (25fps, 75gop, 2160p h265, KID=1237) v2
 "http://refapp.hbbtv.org/videos/tears_of_steel_2160psr_25f75g6sv2/manifest.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_2160psr_25f75g6sv2/drm/manifest.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_2160psr_25f75g6sv2/drm/manifest_subib.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_2160psr_25f75g6sv2/drm/manifest_subob.mpd",
 "http://refapp.hbbtv.org/videos/tears_of_steel_2160psr_25f75g6sv2/drm/manifest_clearkey.mpd",
 # Spring (25fps, 75gop, 1920x804(2.40) h264, KID=148D) v1
 "http://refapp.hbbtv.org/videos/spring_804p_v1/manifest.mpd",
 "http://refapp.hbbtv.org/videos/spring_804p_v1/drm/manifest.mpd",
 # LiveSIM Caminandes 02, Gran Dillama (25fps, 25gop, 2sec, multi MOOF/MDAT, 1080p, KID=1236) v2
 "http://refapp.hbbtv.org/livesim/02_llamav2/manifest.mpd",
 "http://refapp.hbbtv.org/livesim/02_llamadrmv2/manifest.mpd",
 # LiveSIM Caminandes 02, Gran Dillama (25fps, 25gop, 2sec, multi MOOF/MDAT, 1080p, KID=1236) v5
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f25g2sv5/manifest.mpd",
 "http://refapp.hbbtv.org/videos/02_gran_dillama_1080p_25f25g2sv5/drm/manifest.mpd"
]

MPEGCMAFManifests=[
 "https://usp-cmaf-test.s3.eu-central-1.amazonaws.com/tears-of-steel-hevc-only.mpd",
 "https://usp-cmaf-test.s3.eu-central-1.amazonaws.com/tears-of-steel-ttml.mpd",
 "https://usp-cmaf-test.s3.eu-central-1.amazonaws.com/tears-of-steel.mpd"
]

# screen scraped from https://testassets.dashif.org/
DASHIFManifests=[
 "https://dash.akamaized.net/dash264/TestCasesUHD/2b/11/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesUHD/2a/11/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/adapatationSetSwitching/5/manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/multiplePeriods/2/manifest_multiple_Periods_Add_Remove_AdaptationSet.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/multiplePeriods/1/manifest_multiple_Periods_Add_Remove_Representation.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/6/manifest_alternative_lang.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/4/manifest_alternative_Essentialproperty_live.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/1/manifest_alternative_content_live.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/3/manifest_alternative_maxWidth_live.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/2/manifest_alternative_content_ondemand.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/7/360_VR_BavarianAlpsWimbachklamm-AlternativeContent-with-ViewPoint.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/associative_content/1/manifest_associated_content_live.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/xHE-AAC_Stereo/2/Sintel/sintel_audio_video_brs.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/xHE-AAC_Stereo/1/Sintel/sintel_audio_only_brs.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/xHE-AAC_Stereo/3/Sintel/sintel_audio_only_64kbps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/CMAF/UnifiedStreaming/ToS_AVC_MultiRate_MultiRes_AAC_Eng_WebVTT.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2c/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2c/qualcomm/2/MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2b/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2b/qualcomm/2/MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2b/DTV/1/live.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2b/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2b/qualcomm/2/MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2c/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2a/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCases/2a/qualcomm/2/MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2a/qualcomm/1/MultiResMPEG2.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/2a/qualcomm/2/MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1b/qualcomm/1/MultiRatePatched.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1b/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1c/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1c/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1b/qualcomm/1_1/MultiRatePatched.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1a/netflix/exMPD_BIP_TC1.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1a/netflix/exMPD_BIP_TC1.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1a/sony/SNE_DASH_SD_CASE1A_REVISED.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1a/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/1a/qualcomm/2/MultiRate.mpd",
 "https://akamai-axtest.akamaized.net/routes/lapd-v1-acceptance/www_c4/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v8-MultiContent/Clear/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_AudioOnly_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_1080p_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_AudioOnly_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_1080p_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_AudioOnly_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_1080p_ClearKey.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/WSSReporting-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/httpsReporting-Conf-OK-MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesNegative/2/1.mpd",
 "https://dash.akamaized.net/dash264/TestCasesNegative/2/2.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Clear/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Clear/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Encrypted_Cbcs/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Encrypted_Cenc/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Encrypted_Cenc/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v9-MultiFormat/Encrypted_Cbcs/Manifest_1080p.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/multiplePeriods/4/manifest_multiple_Periods_Different_SegmentDuration.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/6/DashIf-HDR10_UHD.mpd", 
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/6/DashIf-SDR_UHD.mpd", 
 "http://54.72.87.160/stattodyn/statodyn.php?type=mpd&pt=1376172180&tsbd=120&origmpd=https%3A%2F%2Fdash.akamaized.net%2Fdash264%2FTestCases%2F1b%2Fqualcomm%2F2%2FMultiRate.mpd&php=http%3A%2F%2Fdasher.eu5.org%2Fstatodyn.php&mpd=&debug=0&hack=.mpd",
 "http://54.72.87.160/stattodyn/statodyn.php?type=mpd&pt=1376172390&tsbd=120&origmpd=http%3A%2F%2Fdash.akamaized.net%2Fdash264%2FTestCases%2F1b%2Fqualcomm%2F2%2FMultiRate.mpd&php=http%3A%2F%2Fdasher.eu5.org%2Fstatodyn.php&mpd=&debug=0&hack=.mpd",
 "http://54.72.87.160/stattodyn/statodyn.php?type=mpd&pt=1376172485&tsbd=10&origmpd=http%3A%2F%2Fdash.akamaized.net%2Fdash264%2FTestCases%2F1b%2Fqualcomm%2F1%2FMultiRatePatched.mpd&php=http%3A%2F%2Fdasher.eu5.org%2Fstatodyn.php&mpd=&debug=0&hack=.mpd",
 "https://dash.akamaized.net/dash264/TestCasesNegative/1/1.mpd",
 "https://dash.akamaized.net/dash264/TestCasesNegative/1/2.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/MPDChaining/fallback_chain/1/manifest_fallback_MPDChaining.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/MPDChaining/fallback_chain/2/manifest_terminationEvent_fallback_MPDChaining.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/15/tos_live_multires_10bit_hev.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/17/bbb_live_multires_10bit_hev.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2a/12/tos_ondemand_multires_10bit_hev.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1a/5/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1b/5/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHDR/3b/3/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHDR/3a/3/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/16/tos_live_multires_10bit_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/18/bbb_live_multires_10bit_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2a/13/tos_ondemand_multires_10bit_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/14/tos_live_multires_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2a/11/tos_ondemand_multires_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1b/10/tos_live_multirate_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1a/9/tos_ondemand_multirate_hvc.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/CMAF/UnifiedStreaming/ToS_HEVC_MultiRate_MultiRes_AAC_Eng_TTML.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/CMAF/UnifiedStreaming/ToS_HEVC_MultiRate_MultiRes_AAC_Eng_WebVTT.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/1/TOS_Live_HEVC_MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2b/2/BBB_Live_HEVC_MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2a/1/TOS_OnDemand_HEVC_MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/2a/2/BBB_OnDemand_HEVC_MultiRes.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1b/1/TOS_Live_HEVC_MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1b/2/BBB_Live_HEVC_MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1a/1/TOS_OnDemand_HEVC_MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHEVC/1a/2/BBB_OnDemand_HEVC_MultiRate.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/HTTPHeader-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/HTTP-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/https-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/httpsQuery-OK-MultiRes.mpd",
 "https://dash.akamaized.net/dash264/CTA/imsc1/IT1-20171027_dash.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/LastSegmentNumber/1/manifest_last_segment_num.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/xlink_30/insertad_2/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/xlink_30/insertad_4/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/start_1800/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/xlink_30/insertad_5/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/scte35_2/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/mup_300/tsbd_500/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/baseurl_d40_u20/baseurl_u40_d20/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/baseurl_u10_d20/baseurl_d10_u20/periods_10/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/periods_20/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/continuous_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/etp_30/etpDuration_10/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/etp_30/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_0/peroff_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_2/peroff_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/scte35_2/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/segtimeline_1/testpic_6s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/segtimeline_1/testpic_6s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/modulo_10/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/utc_direct-head/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/utc_ntp/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/utc_sntp/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/xlink_30/insertad_3/testpic_2s/Manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesUHD/2b/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesUHD/2b/3/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesUHD/2b/4/MultiRate.mpd",
 "https://livesim.dashif.org/livesim-dev/periods_60/xlink_30/insertad_1/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/chunkdur_1/ato_7/testpic4_8s/Manifest300.mpd",
 "https://livesim.dashif.org/livesim/chunkdur_1/ato_7/testpic4_8s/Manifest.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/httpsReporting-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/WSSReporting-OK-MultiRes.mpd",
 "https://livesim.dashif.org/livesim/periods_60/mpdcallback_30/testpic_2s/Manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEGH_Stereo_lc_mha1/1/Sintel/sintel_audio_video_mpegh_mha1_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/1/1/ChID_voices_51_256_ddp.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/9/Living_Room_1080p_51_192k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/11/Living_Room_1080p_51_192k_320k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/10/Living_Room_1080p_51_192k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/12/Living_Room_1080p_51_192k_320k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/7/Living_Room_1080p_20_96k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/8/Living_Room_1080p_20_96k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/3/Living_Room_1080p_51_192k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/5/Living_Room_1080p_51_192k_320k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/4/Living_Room_1080p_51_192k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/6/Living_Room_1080p_51_192k_320k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/1/Living_Room_1080p_20_96k_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesDolby/2/Living_Room_1080p_20_96k_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/4/1/ChID_voices_71_384_448_768_ddp.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/2/1/ChID_voices_71_768_ddp.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dolby/3/1/ChID_voices_20_128_ddp.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/3/Paint_dtsc_testD.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/1/Paint_dtsc_testA.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/3/Paint_dtse_testD.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/1/Paint_dtse_testA.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/3/Paint_dtsh_testD.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/1/Paint_dtsh_testA.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/3/Paint_dtsl_testD.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/1/Paint_dtsl_testA.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/2/Paint_dtsc_testB.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/2/Paint_dtse_testB.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/dts/2/Paint_dtsl_testB.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/HE-AACv2_Multichannel/1/6chID/6chId_480p_single_adapt_heaac5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/HE-AACv2_Multichannel/2/8chID/8ch_id_480p_single_adapt_heaac7_1_cf12_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/HE-AACv2_Multichannel/3/ElephantsDream_6ch/elephants_dream_480p_heaac5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/HE-AACv2_Multichannel/3/Sintel_6ch/sintel_480p_heaac5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/HE-AACv2_Multichannel/3/Sintel_8ch/sintel_480p_heaac7_1_cf12_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEG_Surround/1/6chID/6chId_480p_single_adapt_mps5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEG_Surround/2/ElephantsDream_6ch/elephants_dream_480p_mps5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEG_Surround/2/Sintel_6ch/sintel_480p_mps5_1_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEGH_51_lc_mha1/1/Sintel/sintel_audio_video_mpegh_mha1_5_1_brs_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEGH_714_lc_mha1/1/Sintel/sintel_audio_video_mpegh_mha1_7_1_4_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesMCA/fraunhofer/MPEGH_Stereo_lc_mha1/1/Sintel/sintel_audio_video_mpegh_mha1_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1b.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1f.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1f.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1d.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1c.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1a.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1d.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1e.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/5_1e.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest_MultiPeriod_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest_MultiPeriod.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest_MultiPeriod_AudioOnly.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/sony/SNE_DASH_CASE3B_SD_REVISED.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/aac-lc_stereo_with_video/ElephantsDream/elephants_dream_480p_aaclc_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/aac-lc_stereo_with_video/Sintel/sintel_480p_aaclc_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/aac-lc_stereo_without_video/ElephantsDream/elephants_dream_audio_only_aaclc_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/aac-lc_stereo_without_video/Sintel/sintel_audio_only_aaclc_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/heaac_stereo_without_video/ElephantsDream/elephants_dream_audio_only_heaac_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/heaac_stereo_without_video/Sintel/sintel_audio_only_heaac_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/heaacv2_stereo_without_video/ElephantsDream/elephants_dream_audio_only_heaacv2_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3a/fraunhofer/heaacv2_stereo_without_video/Sintel/sintel_audio_only_heaacv2_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/heaac_stereo_with_video/ElephantsDream/elephants_dream_480p_heaac_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/heaac_stereo_with_video/Sintel/sintel_480p_heaac_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/heaacv2_stereo_with_video/ElephantsDream/elephants_dream_480p_heaacv2_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCases/3b/fraunhofer/heaacv2_stereo_with_video/Sintel/sintel_480p_heaacv2_stereo_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/multiplePeriods/3/manifest_multiple_Periods_Content_Offering_CDN.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1b.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5a/nomor/1.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5a/nomor/3.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5a/nomor/5.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/3.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5a/nomor/4.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/1.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/2.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/6.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/7.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/10.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/11.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/4.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/5.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/8.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5b/nomor/9.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1c.mpd",
 "https://dash.akamaized.net/dash264/TestCases/5c/nomor/4_1a.mpd",
 "https://dash.akamaized.net/dash264/TestCases/4b/qualcomm/2/TearsOfSteel_onDem5secSegSubTitles.mpd",
 "https://dash.akamaized.net/dash264/TestCases/4b/qualcomm/1/ED_OnDemand_5SecSeg_Subtitles.mpd",
 "https://dash.akamaized.net/dash264/TestCases/10a/1/iis_forest_short_poem_multi_lang_480p_single_adapt_aaclc_sidx.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/adapatationSetSwitching/4/manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/adapatationSetSwitching/2/manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesUHD/2a/5/MultiRate.mpd",
 "https://media.axprod.net/TestVectors/v8-MultiContent/Encrypted/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_AudioOnly.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_AudioOnly.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_AudioOnly.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_AudioOnly.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_AudioOnly.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_AudioOnly.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/adapatationSetSwitching/3/manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/adapatationSetSwitching/1/manifest.mpd",
 "https://livesim.dashif.org/livesim/testpic_2s/Manifest.mpd#t=posix:1465406946",
 "https://livesim.dashif.org/livesim/testpic_2s/Manifest.mpd#t=posix:now",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/MPDChaining/regular_chain/1/manifest_regular_MPDChaining_live.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/MPDChaining/regular_chain/2/manifest_regular_MPDChaining_OnDemand.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP33/resolveToZero/1/manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCases/4b/qualcomm/3/Solekai.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest_1080p.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest.mpd",
 "https://media.axprod.net/TestVectors/v7-Clear/Manifest_AudioOnly.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/1a/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/1a/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/1b/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/4c/1/dash.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/1b/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/1c/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/MultiPeriod_OnDemand/ThreePeriods/ThreePeriod_OnDemand2.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/MultiPeriod_OnDemand/ThreePeriods/ThreePeriod_OnDemand_presentationDur.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/MultiPeriod_OnDemand/ThreePeriods/ThreePeriod_OnDemand_presentationDur_AudioTrim.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_AVC_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_AVC_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_HEVC_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_HEVC_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_MultiCodec_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/CMS/Axinom-CMS_MultiCodec_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_AVC_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_AVC_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_HEVC_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_HEVC_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_MultiCodec_MultiRes_MultiRate_25fps.mpd",
 "https://dash.akamaized.net/dash264/TestAdvertising/DRM/Axinom-DRM-in-disconnected-environments_MultiCodec_MultiRes_MultiRate_2997fps.mpd",
 "https://dash.akamaized.net/dash264/TestCases/9b/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/9b/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/9c/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/9a/qualcomm/1/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCases/9a/qualcomm/2/MultiRate.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/MultiPeriod_OnDemand/TwoPeriods/TwoPeriod_OnDemand.mpd",
 "https://dash.akamaized.net/dash264/TestCasesHD/MultiPeriod_OnDemand/TwoPeriods/TwoPeriod_OnDemand_presentationDur.mpd",
 "https://dash.akamaized.net/dash264/TestCasesIOP41/MultiTrack/alternative_content/5/manifest_alternative_ToS_Viewpoint.mpd",
 "https://livesim.dashif.org/livesim/utc_direct/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/utc_head/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/utc_ntp/testpic_2s/Manifest.mpd",
 "https://livesim.dashif.org/livesim/utc_sntp/testpic_2s/Manifest.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-hd-adaptive/sintel-vp9-hd-adaptive.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-hd/sintel-vp9-hd.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-hd-hdr/sintel-vp9-hd-hdr.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-hd-encrypted/sintel-vp9-hd-encrypted.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-uhd/sintel-vp9-uhd.mpd",
 "https://dash.akamaized.net/dash264/TestCasesVP9/vp9-uhd-hdr/sintel-vp9-uhd-hdr.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_1080p_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey/Manifest_AudioOnly_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_1080p_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-MultiKey-MultiPeriod/Manifest_AudioOnly_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_1080p_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_ClearKey.mpd",
 "https://media.axprod.net/TestVectors/v7-MultiDRM-SingleKey/Manifest_AudioOnly_ClearKey.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/WS-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/WSS-OK-MultiRes.mpd",
 "https://raw.githubusercontent.com/Dash-Industry-Forum/SAND-Test-Vectors/master/mpd/dash-if/WSSQuery-OK-MultiRes.mpd",
]


DASHIF_dataset_url = "https://raw.githubusercontent.com/Dash-Industry-Forum/Test-Assets-Dataset-Public/master/dataset/data/testvector.json"

class TestManifests(unittest.TestCase):
	def setUp(self):
		self.log = logging.getLogger('MDP_tests')
		logging.basicConfig(stream=sys.stderr, level=logging.INFO)
		self.log.info('Initialising schema')
		self.xsdParser=etree.XMLParser(load_dtd=True, huge_tree=True, resolve_entities=True)
		with open('../DASH-MPD.xsd', 'r') as schema_file:
			self.mpd_schema = etree.XMLSchema(etree.parse(schema_file, self.xsdParser))
#		is_python3 = sys.version_info.major == 3
		self.xmlParser=etree.XMLParser(load_dtd=True, huge_tree=True, resolve_entities=True)


	def check_a_manifest(self, mpdURL, source):
		with self.subTest(msg=mpdURL):		
			self.log.info('Validating {%s} %s', source, mpdURL)	
			mpdRequest=requests.get(mpdURL, allow_redirects=True)	
			self.assertEqual(mpdRequest.status_code, 200, "Request error, expected 200, got %d" % mpdRequest.status_code)
			if mpdRequest.status_code == 200:
				mpd=etree.fromstring((mpdRequest.text).encode('utf8'), self.xmlParser)
				if not self.mpd_schema.validate(mpd):
					self.fail(self.mpd_schema.error_log.filter_from_errors())
			else:
				self.fail("Request error, expected 200, got %d" % mpdRequest.status_code)			

	def loadDASHIFdataset(self):
		self.log.info('Loading DASH-IF dataset')
		self.DASHIFdataset=[]
		DASHIFrequest=requests.get(DASHIF_dataset_url, allow_redirects=True)
		dataset=json.loads(DASHIFrequest.text)
		for item in dataset:
			self.DASHIFdataset.append(item["url"])
			
	def check_manifests(self, mpdList, source):
		for mpdURL in mpdList:
			self.check_a_manifest(mpdURL, source)

			
	def test_DVB(self):
		self.check_manifests(DVBManifests, "DVB")

	def test_HbbTV(self):
		self.check_manifests(HbbTVManifests, "HbbTV")

	def test_MPEG_CMAF(self):
		self.check_manifests(MPEGCMAFManifests, "MPEG CMAF")
		
	def test_DASH_IF_list(self):
	#only check URLS that are not in the loaded DASH-IF dataset
		self.loadDASHIFdataset()
		for mpdURL in DASHIFManifests:
			try:
				x=self.DASHIFdataset.index(mpdURL)
			except ValueError:
				self.check_a_manifest(mpdURL, "DASH-IF Local List")
			else:
				pass
				
	def test_DASH_IF_dataset(self):
		self.loadDASHIFdataset()
		self.check_manifests(self.DASHIFdataset, "DASH-IF Dataset")
		
if __name__ == '__main__':
    unittest.main()
