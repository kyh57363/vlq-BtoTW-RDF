import os,sys,time
from numpy import linspace
from array import array
from ROOT import *
#from weights import *  ## later, get weights.py working for nRun and xSec

# give a branch name to plot
iPlot = sys.argv[1] 

# Samples to process and categories to plot
indir = "/store/user/sxiaohe/vlq-BtoTW-RDF/cut_update1_170/Bprime_hadds/"
outdir = os.getcwd()+'/plots_forwardjet/'
if not os.path.exists(outdir): os.system('mkdir -p '+outdir)
samples = {'Bp800':'Bprime800_hadd.root', 
           'Bp1400':'Bprime1400_hadd.root',
           'Bp2000':'Bprime2000_hadd.root',
           #'qcd200':'QCD200_hadd.root',                                  
           'qcd300':'QCD300_hadd.root',                                  
           'qcd500':'QCD500_hadd.root',                                  
           'qcd700':'QCD700_hadd.root',                                  
           'qcd1000':'QCD1000_hadd.root',                                
           'qcd1500':'QCD1500_hadd.root',                                
           'qcd2000':'QCD2000_hadd.root',
           'ttbar':'ttbar_hadd.root',
           'wjets200':'WJets200_hadd.root',
           'wjets400':'WJets400_hadd.root',
           'wjets600':'WJets600_hadd.root',
           'wjets800':'WJets800_hadd.root',
           'wjets1200':'WJets1200_hadd.root',
           'wjets2500':'WJets2500_hadd.root',
           'singleT':'singleT_hadd.root',
           'singleTb':'singleTb_hadd.root',
           'data_obs':'ttbar_hadd.root' # data is a copy of ttbar for now, need histograms in the file for limits
}
tags = {'tjet':'taggedTjet == 1',
        'Wjet':'taggedWjet == 1',
        'Wbjet':'taggedWbjetJet == 1',
        'other':'isValidBDecay < 1', # later likely some other selection like a network score
        'all':'isValidBDecay == 1', # combine all tagged events
        'genLeptonicT':'trueLeptonicMode == 1',
        'genLeptonicW':'trueLeptonicMode == 0',
        'trueSingleLepT':'leptonicParticle == 1 && trueLeptonicMode == 1',
        'trueSingleLepW':'leptonicParticle == 0 && trueLeptonicMode == 0',
        'falseSingleLepW':'leptonicParticle == 0 && trueLeptonicMode == 1',
        'falseSingleLepT':'leptonicParticle == 1 && trueLeptonicMode == 0',
        'correctTag':'(taggedTjet == 1 && trueLeptonicMode == 1) && (taggedWjet == 1 && trueLeptonicMode == 0)',
        'flippedTag':'(taggedTjet == 1 && trueLeptonicMode == 0) && (taggedWjet == 1 && trueLeptonicMode == 1)'
    }

# Numbers to weight the samples relative to each other
lumi = 138000.0
nRun = {'Bp800':99800.,
        'Bp1400':99600.,
        'Bp2000':99600.,  # fixme, need a sum-of-gen-weights calculated...
        #'qcd200':61542214.,
        'qcd300':56214199.,
        'qcd500':61097673.,
        'qcd700':47314826.,
        'qcd1000':15230975.,
        'qcd1500':11887406.,
        'qcd2000':5710430.,
        'ttbar':476408000.,
        'wjets200':58225632.,
        'wjets400':7444030.,
        'wjets600':7718765.,
        'wjets800':7306187.,
        'wjets1200':6481518.,
        'wjets2500':2097648.,
        'singleT':178336000.,
        'singleTb':95627000.,
        'data_obs':1}
xsec = {'Bp800':1.0,'Bp1400':1.0,'Bp2000':1.0, #signals all the same at 1pb for now, predictions vary
        #'qcd200':1712000,
        'qcd300':347700,
        'qcd500':32100,
        'qcd700':6831,
        'qcd1000':1207,
        'qcd1500':119.9,
        'qcd2000':25.24,
        'ttbar':831.76*0.438,
        'wjets200':359.7*1.21,
        'wjets400':48.91*1.21,
        'wjets600':12.05*1.21,
        'wjets800':5.501*1.21,
        'wjets1200':1.329*1.21,
        'wjets2500':0.03216*1.21,
        'singleT':136.02,
        'singleTb':80.95,
        'data_obs':1}

# Settings for drawing the graphs
sig1leg='B (0.8 TeV)'
sig2leg='B (2.0 TeV)'
sig3leg='B (1.4 TeV)'
sigScaleFact = 1 # zoom in/out on signal
print 'Scale factor = ',sigScaleFact
bkgProcList = [#'qcd200',
'qcd300','qcd500','qcd700','qcd1000','qcd1500','qcd2000','wjets200','wjets400','wjets600','wjets800','wjets1200','wjets2500','ttbar','singleT','singleTb']
bkgHistColors = {#'qcd200':kOrange-5,
'qcd300':kOrange-5,'qcd500':kOrange-5,'qcd700':kOrange-5,'qcd1000':kOrange-5,'qcd1500':kOrange-5,'qcd2000':kOrange-5,
                 'ttbar':kAzure+8,
                 'wjets200':kMagenta-2,'wjets400':kMagenta-2,'wjets600':kMagenta-2,'wjets800':kMagenta-2,'wjets1200':kMagenta-2,'wjets2500':kMagenta-2,
                 'singleT':kGreen-3,'singleTb':kGreen-3,} #TT
yLog  = True
blind = True
lumiSys = 0.20 # 20% uncertainty on background
doPlotting = True

# Settings for different iPlots
plotList = {#discriminantName:(discriminantLJMETName, binning, xAxisLabel)
    'lepPt' :('lepton_pt',linspace(0, 1000, 51).tolist(),';Lepton p_{T} [GeV]'),
    'lepEta':('lepton_eta',linspace(-4, 4, 41).tolist(),';Lepton #eta'),
    'lepPhi':('lepton_phi',linspace(-3.2,3.2,65).tolist(),';#phi(l)'),
    'lepIso':('lepton_miniIso',linspace(0,0.2,51).tolist(),';lepton mini isolation'),

    'JetEta':('gcJet_eta',linspace(-4, 4, 41).tolist(),';AK4 jet #eta'),
    'JetPt' :('gcJet_pt',linspace(0, 1500, 51).tolist(),';AK4 jet p_{T} [GeV]'),
    'NJetsCentral' :('NJets_central',linspace(0, 20, 21).tolist(),';central jet multiplicity'),
    'NJetsForward' :('NJets_forward',linspace(0, 20, 21).tolist(),';forward jet multiplicity'),
    'NBJets':('NJets_DeepFlavM',linspace(0, 10, 11).tolist(),';b tag multiplicity'),
    'MET'   :('MET_pt',linspace(0, 1500, 51).tolist(),';#slash{E}_{T} [GeV]'),
    'HT':('Jet_HT',linspace(0, 5000, 51).tolist(),';H_{T} (GeV)'),
    'ST':('Jet_ST',linspace(0, 5000, 51).tolist(),';S_{T} (GeV)'),

    'FatJetEta':('gcFatJet_eta',linspace(-4, 4, 41).tolist(),';AK8 jet #eta'),
    'FatJetPt' :('gcFatJet_pt',linspace(0, 1500, 51).tolist(),';AK8 jet p_{T} [GeV]'),
    'Tau21'  :('tau21',linspace(0, 1, 51).tolist(),';AK8 Jet #tau_{2}/#tau_{1}'),
    'SoftDrop' :('FatJet_sdMass',linspace(0, 500, 51).tolist(),';AK8 soft drop mass [GeV]'),
    'probj':('pNet_J',linspace(0,1,51).tolist(),';particleNet J score'),
    'probt':('pNet_T',linspace(0,1,51).tolist(),';particleNet t score'),
    'probw':('pNet_W',linspace(0,1,51).tolist(),';particleNet W score'),
    'deeptag':('pNet_tag',linspace(0,10,11).tolist(),';particleNet tag (0 = J, 1 = t, 2 = W)'),
    'NFatJets':('NFatJets',linspace(0, 10, 11).tolist(),';AK8 jet multiplicity'),
    'nT':('nT_DeepAK8',linspace(0,5,6).tolist(),';N particleNet t-tagged jets'),
    'nW':('nW_DeepAK8',linspace(0,5,6).tolist(),';N particleNet W-tagged jets'),
    'minDR_twoAK8s':('minDR_leadAK8otherAK8',linspace(0,5,51).tolist(),';min #Delta R(leading AK8 jet, other AK8 jet) [GeV]'),

    'tmass':('t_mass',linspace(0,500,51).tolist(),';M(t) [GeV]'),
    'tpt':('t_pt',linspace(0,1000,51).tolist(),';p_{T}(t) [GeV]'),
    'Wdrlep':('DR_W_lep',linspace(0,5,51).tolist(),';leptonic W, #DeltaR(W,lepton)'),
    'tdrWb':('DR_W_b',linspace(0,6.3,51).tolist(),';leptonic t, #DeltaR(W,b)'),
    'isLepW':('leptonicParticle',linspace(0,2,3).tolist(),';lepton from W'),
    'WMt':('W_MT',linspace(0,1500,51).tolist(),';M_{T}(W) [GeV]'),
    'minMlj':('minMleppJet',linspace(0,1000,51).tolist(),';min[M(l,jet)] [GeV], 0 b tags'),
    'PtRel':('ptRel_lep_Jet',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest jet) [GeV]'),
    'PtRelAK8':('ptRel_lep_FatJet',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest AK8 jet) [GeV]'),
    'minDR':('minDR_lep_Jet',linspace(0,5,51).tolist(),';#Delta R(l, closest jet) [GeV]'),
    'minDRAK8':('minDR_lep_FatJet',linspace(0,5,51).tolist(),';#Delta R(l, closest AK8 jet) [GeV]'),

    'BpMass':('Bprime_mass',linspace(0,4000,51).tolist(),';M(B) [GeV]'),
    #'BpMass':('Bprime_mass',51,0,4000,';M(B) [GeV]'),
    'BpPt':('Bprime_pt',linspace(0,3000,51).tolist(),';B quark p_{T} [GeV]'),
    'BpEta':('Bprime_eta',linspace(-5,5,51).tolist(),';B quark #eta'),
    'BpPhi':('Bprime_phi',linspace(-3.14,3.14,51).tolist(),';B quark #phi'),
    'BpDeltaR':('Bprime_DR',linspace(0,5,51).tolist(),';#DeltaR(B quark product jets)'),
    'BpPtBal':('Bprime_ptbal',linspace(0,3,51).tolist(),';B quark t/W p_{T} ratio'),
    'BpChi2':('Bprime_chi2',linspace(0,1000,51).tolist(),';B quark reconstruction #chi^{2}'), # CHECK ME, what range?

    'mlp_HT500_Bprime':('mlp_HT500_Bprime',linspace(0,1,51).tolist(),';MLP (HT 500) T score'), # later, these should exist
    'mlp_HT500_TTbar': ('mlp_HT500_TTbar',linspace(0,1,51).tolist(),';MLP (HT 500) t#bar{t} score'),
    'mlp_HT500_WJets': ('mlp_HT500_WJets',linspace(0,1,51).tolist(),';MLP (HT 500) W+jets score'),
    'mlp_HT250_Bprime':('mlp_HT250_Bprime',linspace(0,1,51).tolist(),';MLP (HT 250) T score'), # later, these should exist
    'mlp_HT250_TTbar': ('mlp_HT250_TTbar',linspace(0,1,51).tolist(),';MLP (HT 250) t#bar{t} score'),
    'mlp_HT250_WJets': ('mlp_HT250_WJets',linspace(0,1,51).tolist(),';MLP (HT 250) W+jets score'),

    "Bprime_gen_pt":('Bprime_gen_pt',linspace(0,1500,51).tolist(),';B quark p_{T gen} [GeV]'),
    "Bprime_gen_eta":('Bprime_gen_eta',linspace(-10,10,51).tolist(),';B quark #eta _{gen}'),
    "Bprime_gen_phi":('Bprime_gen_phi',linspace(-3.5,3.5,51).tolist(),';B quark #phi _{gen}'),
    "Bprime_gen_mass":('Bprime_gen_mass',linspace(700,2300,51).tolist(),';M_{gen}(B) [GeV]'),

    "t_gen_pt":('t_gen_pt',linspace(0,1800,51).tolist(),';p_{T gen}(t) [GeV]'),
    "t_gen_eta":('t_gen_eta',linspace(-4,4,51).tolist(),';#eta (t)'),
    "t_gen_phi":('t_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi (t)'),
    "t_gen_mass":('t_gen_mass',linspace(150,200,51).tolist(),';M_{gen}(t) [GeV]'),
    "t_gen_status":('t_gen_status',linspace(20,55,35).tolist(),'particle status(t)'),
    "Del_t":('t_mass - t_gen_mass',linspace(-200, 800, 51).tolist(),';M_{reco}(t)-M_{gen}(t) [GeV]'),

    "daughterb_gen_pt":('daughterb_gen_pt',linspace(0,1200,51).tolist(),';p_{T gen}(b_{t}) [GeV]'),
    "daughterb_gen_eta":('daughterb_gen_eta',linspace(-5,5,51).tolist(),';#eta_{gen}(b_{t})'),
    "daughterb_gen_phi":('daughterb_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi_{gen}(b_{t})'),
    "daughterb_gen_status":('daughterb_gen_status',linspace(20,25,6).tolist(),';particle statuss(b_{t})'),

    "daughterW_gen_pt":('daughterW_gen_pt',linspace(0,1500,51).tolist(),';p_{T gen}(W_{t}) [GeV]'),
    "daughterW_gen_eta":('daughterW_gen_eta',linspace(-5,5,51).tolist(),';#eta_{gen}(W_{t})'),
    "daughterW_gen_phi":('daughterW_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi_{gen}(W_{t})'),
    "daughterW_gen_mass":('daughterW_gen_mass',linspace(30,110,51).tolist(),';M_{gen}(W_{t}) [GeV]'),
    "daughterW_gen_status":('daughterW_gen_status',linspace(20,55,35).tolist(),';particle status(W_{t})'),

    "Tlepton_gen_pt":('Tlepton_gen_pt',linspace(0,1000,51).tolist(),';p_{T gen}(l_{t}) [GeV]'),
    "Tlepton_gen_eta":('Tlepton_gen_eta',linspace(-5,7,51).tolist(),';#eta_{gen}(l_{t})'),
    "Tlepton_gen_phi":('Tlepton_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi_{gen}(l_{t})'),
    "Tlepton_gen_pdgId":('Tlepton_gen_pdgId',linspace(-17,17,35).tolist(),';gen pdgId(l_{t})'),
    "Tlepton_gen_status":('Tlepton_gen_status',linspace(0,25,26).tolist(),';particle status(l_{t})'),

    "W_gen_pt":('W_gen_pt',linspace(0,1800,51).tolist(),';p_{T gen}(W) [GeV]'),
    "W_gen_eta":('W_gen_eta',linspace(-4,5,51).tolist(),';#eta_{gen}(W)'),
    "W_gen_phi":('W_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi_{gen}(W)'),
    "W_gen_mass":('W_gen_mass',linspace(30,110,51).tolist(),';M_{gen}(W) [GeV]'),
    "W_gen_status":('W_gen_status',linspace(20,55,35).tolist(),'gen particle status(W)'),
    "Del_W":('W_mass - W_gen_mass',linspace(-100, 300, 51).tolist(),';M_{reco}(W)-M_{gen}(W) [GeV]'),

    "Wlepton_gen_pt":('Wlepton_gen_pt',linspace(0,1600,51).tolist(),';p_{T gen}(l) [GeV]'),
    "Wlepton_gen_eta":('wlepton_gen_eta',linspace(-4,4,51).tolist(),';#eta_{gen}(l)'),
    "Wlepton_gen_phi":('Wlepton_gen_phi',linspace(-3.5,3.5,51).tolist(),';#phi_{gen}(l)'),
    "Wlepton_gen_pdgId":('Wlepton_gen_pdgId',linspace(-17,17,35).tolist(),'gen pdgId(l)'),
    "Wlepton_gen_status":('Wlepton_gen_status',linspace(0,25,26).tolist(),'gen particle status(l)'),
}

# open an output file for the histos
outputFile = TFile.Open("histos_"+iPlot+".root","RECREATE")

hists = {}
start_time = time.time()
print 'Building histograms...'
for sample in samples.keys():
    print '\t Sample =',sample
    tfile = TFile.Open("root://cmseos.fnal.gov/"+indir+"/"+samples[sample]+"hadd.root")
    ttree = tfile.Get("Events")
    if (sample == 'Bp1400'): # This is to correcct a bug (14000 should be 1400) which hopefully will be irrelevant someday
	tfile2 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/BpM14000_predict_wjet.root")
        tfile3 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/BpM14000_predict_ttbar.root")
    	tfile4 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/BpM14000_predict_bprime.root")
    else:
	tfile2 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/" + samples[sample] + "predict_wjet.root")
        tfile3 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/" + samples[sample] + "predict_ttbar.root")
        tfile4 = TFile.Open("root://cmseos.fnal.gov//store/user/khowey/BpMFiles/" + samples[sample] + "predict_bprime.root")
    # Three trees for each different class get merged into one
    ttree2 = tfile2.Get("Events")
    ttree3 = tfile3.Get("Events")
    ttree4 = tfile4.Get("Events")
    ttree.AddFriend(ttree2)
    ttree.AddFriend(ttree3)
    ttree.AddFriend(ttree4)

    for tag in tags.keys():
        print '\t\t tag =',tag
        histo = TH1D(sample+'_'+tag, plotList[iPlot][2]+';Events / bin',len(plotList[iPlot][1])-1,array('d',plotList[iPlot][1]))
        histo.Sumw2()
        
        weightstr = "(Generator_weight*{}*{}/({}*abs(Generator_weight)))".format(lumi,xsec[sample],nRun[sample])
        ttree.Draw(plotList[iPlot][0]+' >> '+sample+'_'+tag,weightstr+'*(NJets_forward > 0 && Bprime_mass > 0 && Bprime_gen_mass!=-999 && '+tags[tag]+')','GOFF')
        histo.SetDirectory(0)
        hists[sample+'_'+tag] = histo

outputFile.cd()
for tag in tags.keys():
    hists['ttbar_'+tag].Write()
    hists['singleT_'+tag].Add(hists['singleTb_'+tag])
    hists['singleT_'+tag].Write()
    hists['wjets_'+tag] = hists['wjets200_'+tag].Clone('wjets_'+tag)
    hists['wjets_'+tag].Add(hists['wjets400_'+tag])
    hists['wjets_'+tag].Add(hists['wjets600_'+tag])
    hists['wjets_'+tag].Add(hists['wjets800_'+tag])
    hists['wjets_'+tag].Add(hists['wjets1200_'+tag])
    hists['wjets_'+tag].Add(hists['wjets2500_'+tag])
    hists['wjets_'+tag].Write()
    #hists['data_obs_'+tag].Write()
    hists['Bp800_'+tag].Write()
    hists['Bp1400_'+tag].Write()
    hists['Bp2000_'+tag].Write()
outputFile.Close();

plot_time = time.time()
#print histos

#hists = {}
if doPlotting:

    print 'Plotting...',iPlot

    #for iPtr in histos.keys():
    #    hists[iPtr] = histos[iPtr].GetValue()

    #print hists

    for tag in tags.keys():
        print '\t tag =',tag

        histPrefix = iPlot+'_'+tag
        
        # add the backgrounds together
        bkgHT = hists['ttbar_'+tag].Clone()
        for proc in bkgProcList:
            if proc == 'ttbar': continue
            bkgHT.Add(hists[proc+'_'+tag])

        # set a larger uncertainty
        for ibin in range(1,bkgHT.GetNbinsX()+1):
            bkgHT.SetBinError(ibin,bkgHT.GetBinContent(ibin)*lumiSys)

        
        hsig800 = hists['Bp800_'+tag]
        hsig1400 = hists['Bp1400_'+tag]
        hsig2000 = hists['Bp2000_'+tag]
        if bkgHT.Integral() != 0:
            if hsig2000.Integral()/bkgHT.Integral() > 0.1: sigScaleFact = 1
        hsig800.Scale(sigScaleFact)
        hsig1400.Scale(sigScaleFact)
        hsig2000.Scale(sigScaleFact)
        
        ############################################################
        ############## Making Plots of e+jets, mu+jets and e/mu+jets 
        ############################################################
    
        stackbkgHT = THStack("stackbkgHT","")
        # set each background a different color
        for proc in bkgProcList:
            stackbkgHT.Add(hists[proc+'_'+tag])
            hists[proc+'_'+tag].SetLineColor(bkgHistColors[proc])
            hists[proc+'_'+tag].SetFillColor(bkgHistColors[proc])
            hists[proc+'_'+tag].SetLineWidth(2)

        sig1Color= kBlack
        sig2Color= kBlack
        sig3Color= kBlack

        hsig800.SetLineColor(sig1Color)
        hsig800.SetFillStyle(0)
        hsig800.SetLineWidth(3)
        hsig1400.SetLineColor(sig2Color)
        hsig1400.SetLineStyle(5)
        hsig1400.SetFillStyle(0)
        hsig1400.SetLineWidth(3)
        hsig2000.SetLineColor(sig2Color)
        hsig2000.SetLineStyle(7)#5)
        hsig2000.SetFillStyle(0)
        hsig2000.SetLineWidth(3)
    
        bkgHT.SetFillStyle(3004)
        bkgHT.SetFillColor(kBlack)
    
        gStyle.SetOptStat(0)
        c1 = TCanvas("c1","c1",1200,1000)
        gPad.SetTopMargin(0.08)
        gPad.SetRightMargin(0.04)
        gPad.SetBottomMargin(0.12)
        gPad.SetLeftMargin(0.11)

        bkgHT.GetYaxis().CenterTitle()
        if yLog:
            gPad.SetLogy()
            bkgHT.SetMinimum(0.101)
            bkgHT.SetMaximum(200*bkgHT.GetMaximum())

        bkgHT.GetXaxis().SetTitleOffset(1.1)

        bkgHT.Draw("E2")
        stackbkgHT.Draw("same HIST")
        hsig800.Draw("SAME HIST")
        hsig2000.Draw("SAME HIST")
        hsig1400.Draw("SAME HIST")
        bkgHT.Draw("SAME E2")
    
        leg = TLegend(0.50,0.64,0.89,0.89)
        leg.SetShadowColor(0)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetLineColor(0)
        leg.SetLineStyle(0)
        leg.SetBorderSize(0) 
        leg.SetNColumns(2)
        leg.SetTextFont(62)#42)
        scaleFact1Str = ''#' x'+str(sigScaleFact)
        scaleFact2Str = ''#' x'+str(sigScaleFact)
    
        leg.AddEntry(hsig800,sig1leg+scaleFact1Str,"l") #left
        leg.AddEntry(hists['ttbar_'+tag],"t#bar{t}","f") #right
        leg.AddEntry(hsig1400,sig3leg+scaleFact2Str,"l") #left
        leg.AddEntry(hists['wjets200_'+tag],"W+jets","f") #right
        leg.AddEntry(hsig2000,sig2leg+scaleFact2Str,"l") #left
        leg.AddEntry(hists['singleT_'+tag],"single t","f") #right
        leg.AddEntry(bkgHT,"Bkg. uncert.","f") #left
        
        leg.Draw("same")
        
        prelimTex2=TLatex()
        prelimTex2.SetNDC()
        prelimTex2.SetTextFont(61)
        prelimTex2.SetLineWidth(2)
        prelimTex2.SetTextSize(0.08)
        if blind: prelimTex2.SetTextSize(0.08)
        prelimTex2.DrawLatex(0.12,0.93,"CMS")
        
        prelimTex3=TLatex()
        prelimTex3.SetNDC()
        prelimTex3.SetTextAlign(12)
        prelimTex3.SetTextFont(52)
        prelimTex3.SetTextSize(0.055)
        prelimTex3.SetLineWidth(2)
        if blind: prelimTex3.DrawLatex(0.26,0.945,"Simulation work in progress") #"Preliminary")
        
        # making up names of the image files, making the folder exists, and doing SaveAs
        savePrefix = outdir+histPrefix
        if yLog: savePrefix+='_logy'
        #c1.SaveAs(savePrefix+".pdf")
        c1.SaveAs(savePrefix+".png")
        c1.SaveAs(savePrefix+".root")

print("--- %s min for hists, %s s for plots ---" % (round(plot_time - start_time, 2)/60, round(time.time() - plot_time, 2)))
    


