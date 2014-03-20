

Execution d'une s�rie d'exp�riences
___________________________________
===================================

- Editer SocialNetwork.evm (ou le fichier .evm appropri�)

Localement :
==========
- Fabriquer '_Params.evo' en lan�ant 
	e:\recherch\Evopy\Expe\EvoGen.py SocialNetwork.evo SocialNetwork.evm _Params.evo
- Lancer une exp�rience avec SocialNetwork.py  qui lit '_Params.evo'
- Possibilit� de lancer plusieurs exp�riences en batch en d�finissant BatchMode � 1

De mani�re distante:
===================

- Transporter tout Evolife (ou tout ce qui pertinent, obtenu par Copytree) sur le repertoire d'experience
- Transporter les fichiers utiles de Evopy/Expe sur le repertoire d'experience
- Editer launchPythonJobs.sh pour donner les bons arguments a go.sh
- Eventuellement, remonter au repertoire Evolife et faire:  "python first"
- revenir sur le repertoire d'experience et faire ./launchPythonJobs.sh
- tester que les jobs tournent par ./chkPythonJobs.sh
- Faire 'touch fini' pour arr�ter proprement la boucle des jobs
- Faire 'touch stop' pour arr�ter les jobs en urgence. Attention, 
  les fichiers .res de r�sultats peuvent �tre inexploitables
  (voir le num�ro de la derni�re it�tation en fin de deuxi�me ligne).
- ramener les fichiers de r�sultats  *.res
- penser � ramener les fichiers .sh et .evm s'ils ont �t� modifi�s

Traitement des r�sultats:
========================

- Editer Get_Expe.py en modifiant la contrainte 'Filter'
  (car le programme ne g�re apr�s qu'une seule variable <param>)
- Aller sur le r�pertoire des r�sultats.
- lancer ...Get_Expe.py *.res <param>. Le programme engendre des *.dat
- copier le fichier .dat qui nous int�resse sur ..\Courbes.dat
- lancer ou actualiser Signals.xls ou courbe.xls
- Eventuellement, copier la ligne Signal ou SignalInvestment (en valeurs) dans 
  un autre fichier, comme e:\pubr\Evolcom\ScienceEvolcom\Figure SignalInvestment_SC_MaxFol=3_BC=0.xls

