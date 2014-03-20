

Execution d'une série d'expériences
___________________________________
===================================

- Editer SocialNetwork.evm (ou le fichier .evm approprié)

Localement :
==========
- Fabriquer '_Params.evo' en lançant 
	e:\recherch\Evopy\Expe\EvoGen.py SocialNetwork.evo SocialNetwork.evm _Params.evo
- Lancer une expérience avec SocialNetwork.py  qui lit '_Params.evo'
- Possibilité de lancer plusieurs expériences en batch en définissant BatchMode à 1

De manière distante:
===================

- Transporter tout Evolife (ou tout ce qui pertinent, obtenu par Copytree) sur le repertoire d'experience
- Transporter les fichiers utiles de Evopy/Expe sur le repertoire d'experience
- Editer launchPythonJobs.sh pour donner les bons arguments a go.sh
- Eventuellement, remonter au repertoire Evolife et faire:  "python first"
- revenir sur le repertoire d'experience et faire ./launchPythonJobs.sh
- tester que les jobs tournent par ./chkPythonJobs.sh
- Faire 'touch fini' pour arrêter proprement la boucle des jobs
- Faire 'touch stop' pour arrêter les jobs en urgence. Attention, 
  les fichiers .res de résultats peuvent être inexploitables
  (voir le numéro de la dernière itétation en fin de deuxième ligne).
- ramener les fichiers de résultats  *.res
- penser à ramener les fichiers .sh et .evm s'ils ont été modifiés

Traitement des résultats:
========================

- Editer Get_Expe.py en modifiant la contrainte 'Filter'
  (car le programme ne gère après qu'une seule variable <param>)
- Aller sur le répertoire des résultats.
- lancer ...Get_Expe.py *.res <param>. Le programme engendre des *.dat
- copier le fichier .dat qui nous intéresse sur ..\Courbes.dat
- lancer ou actualiser Signals.xls ou courbe.xls
- Eventuellement, copier la ligne Signal ou SignalInvestment (en valeurs) dans 
  un autre fichier, comme e:\pubr\Evolcom\ScienceEvolcom\Figure SignalInvestment_SC_MaxFol=3_BC=0.xls

