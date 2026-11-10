# Αναφορά API · έκδοση 1.1.3

Η αναφορά εξάγεται από το πραγματικό OpenAPI. Βάση URL:`/api/v1`. Τα ακριβή σώματα, πεδία, όρια και μοντέλα απαντήσεων βρίσκονται στο [OpenAPI](../koino/openapi.json). Παραδείγματα,ρόλοι,χρόνοι και χειρισμός σφαλμάτων στη [σύμβαση διεπαφής](../koino/symvolaio-frontend-backend.md).

| Μέθοδος | Διαδρομή | Λειτουργία | Σχήμα επιτυχίας |
|---|---|---|---|
|GET|`/api/v1/ygeia`|Έλεγχος υγείας του backend και της βάσης SQLite|`YgeiaApantisi`|
|GET|`/api/v1/metadedomena`|Μεταδεδομένα, μονάδες μέτρησης και διαθέσιμα statuses|`MetadedomenaApantisi`|
|POST|`/api/v1/taftopoiisi/eisodos`|Είσοδος χρήστη επίδειξης|`EisodosApantisi`|
|GET|`/api/v1/taftopoiisi/trexwn-xristis`|Πληροφορίες συνδεδεμένου χρήστη|`XristisApantisi`|
|GET|`/api/v1/dikaiwmata/metavivaseis`|Ανάκτηση ισχυουσών μεταβιβάσεων ανά ρόλο και πεδίο|`λίστα MetavivasiApantisi`|
|POST|`/api/v1/dikaiwmata/metavivaseis`|Έγκριση μεταβίβασης από coordinator με audit|`EgkrisiMetavivasisApantisi`|
|POST|`/api/v1/dikaiwmata/metavivaseis/proepiskopisi`|Προεπισκόπηση επιπτώσεων και επιλεξιμότητας μεταβίβασης|`ProepiskopisiMetavivasisApantisi`|
|POST|`/api/v1/dikaiwmata/metavivaseis/{id_metavivasis}/anaklisi`|Ανάκληση εξουσιοδότησης με audit|`AnaklisiMetavivasisApantisi`|
|GET|`/api/v1/synopsi`|Συνοπτική κοινή κατάσταση αποικίας και ενεργοί συναγερμοί|`SynopsiApantisi`|
|GET|`/api/v1/aisthitires`|Λίστα αισθητήρων με προαιρετικό φιλτράρισμα asset/metric|`λίστα AisthitirasApantisi`|
|GET|`/api/v1/aisthitires/{id_aisthitira}/metriseis`|Ιστορικό και ποιότητα μετρήσεων αισθητήρα|`λίστα MetrisiApantisi`|
|GET|`/api/v1/xwroi-katoikisis`|Λίστα κατοικήσιμων χώρων και βασικών μετρήσεων (LIFE-01)|`λίστα XwrosApantisi`|
|GET|`/api/v1/xwroi-katoikisis/{id_xwrou}/katastasi`|Πλήρες snapshot υποστήριξης ζωής θαλάμου (LIFE-02, LIFE-03)|`KatastasiXwrouApantisi`|
|GET|`/api/v1/xwroi-katoikisis/{id_xwrou}/provlepsi-oxygonou`|Πρόβλεψη οξυγόνου και εκτίμηση αυτονομίας (LIFE-04)|`OxygonoApantisi`|
|POST|`/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi`|Προεπισκόπηση αλλαγής θερμοκρασίας χωρίς μεταβολή κατάστασης (LIFE-06, §7)|`ProepiskopisiThermokrasiasApantisi`|
|POST|`/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles`|Επιβεβαίωση και εκτέλεση αλλαγής θερμοκρασίας (LIFE-07)|`EpivevaiwsiThermokrasiasApantisi`|
|GET|`/api/v1/entoles/{id_entolis}`|Ανάκτηση κατάστασης και κύκλου ζωής εντολής (CORE-10)|`EntoliPlirisApantisi`|
|POST|`/api/v1/entoles/{id_entolis}/akyrosi`|Ακύρωση εντολής εφόσον επιτρέπεται (CORE-10)|`AkyrosiEntolisApantisi`|
|POST|`/api/v1/xwroi-katoikisis/{id_xwrou}/syskeves/{id_syskevis}/proepiskopisi`|Προεπισκόπηση θέρμανσης, καθαριστή αέρα ή παραγωγής οξυγόνου|`ProepiskopisiSyskevisApantisi`|
|POST|`/api/v1/xwroi-katoikisis/{id_xwrou}/syskeves/{id_syskevis}/entoles`|Επιβεβαίωση ρύθμισης εξοπλισμού υποστήριξης ζωής|`EpivevaiwsiSyskevisApantisi`|
|GET|`/api/v1/thermokipia`|Pare Thermokipia|`λίστα ThermokipioApantisi`|
|GET|`/api/v1/thermokipia/{id_thermokipiou}/zwnes`|Pare Zwnes Thermokipiou|`λίστα ZwniApantisi`|
|POST|`/api/v1/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi`|Proepiskopisi Ardefsis|`ProepiskopisiArdefsisApantisi`|
|POST|`/api/v1/thermokipia/{id_thermokipiou}/ardefsi/programmata`|Dimiourgia Programmatos Ardefsis|`ArdefsiApantisi`|
|GET|`/api/v1/thermokipia/{id_thermokipiou}/ardefsi/programmata`|Pare Programmata Ardefsis|`λίστα ProgrammaArdefsisApantisi`|
|POST|`/api/v1/ardefsi/programmata/{id_programmatos}/akyrosi`|Akyrosi Ardefsis|`AkyrosiApantisi`|
|POST|`/api/v1/thermokipia/{id_thermokipiou}/fwtismos/proepiskopisi`|Proepiskopisi Fwtismou|`ProepiskopisiFwtismouApantisi`|
|POST|`/api/v1/thermokipia/{id_thermokipiou}/fwtismos/entoles`|Dimiourgia Programmatos Fwtismou|`FwtismosApantisi`|
|GET|`/api/v1/thermokipia/{id_thermokipiou}/fwtismos/programmata`|Pare Programmata Fwtismou|`λίστα ProgrammaFwtismouApantisi`|
|POST|`/api/v1/thermokipia/{id_thermokipiou}/fwtismos/programmata/{id_programmatos}/akyrosi`|Akyrosi Fwtismou|`AkyrosiApantisi`|
|GET|`/api/v1/nero/dexamenes`|Pare Dexamenes Nerou|`NeroApantisi`|
|GET|`/api/v1/nero/isozygio`|Pare Isozygio Nerou|`IsozygioNerouApantisi`|
|GET|`/api/v1/nero/roes`|Pare Roes Nerou|`λίστα RoiApantisi`|
|POST|`/api/v1/nero/anakyklwsi/proepiskopisi`|Proepiskopisi Anakyklwsis|`ProepiskopisiAnakyklwsisApantisi`|
|POST|`/api/v1/nero/anakyklwsi/entoles`|Dimiourgia Programmatos Anakyklwsis|`AnakyklwsiApantisi`|
|POST|`/api/v1/nero/anakyklwsi/programmata`|Dimiourgia Programmatos Anakyklwsis|`AnakyklwsiApantisi`|
|GET|`/api/v1/nero/anakyklwsi/programmata`|Pare Programmata Anakyklwsis|`λίστα ProgrammaAnakyklwsisApantisi`|
|POST|`/api/v1/nero/anakyklwsi/programmata/{id_programmatos}/akyrosi`|Akyrosi Anakyklwsis|`AkyrosiApantisi`|
|GET|`/api/v1/energeia/katastasi`|Pare Katastasi Energeias|`EnergeiaApantisi`|
|GET|`/api/v1/energeia/fortia`|Pare Energeiaka Fortia|`λίστα FortioApantisi`|
|GET|`/api/v1/energeia/fwtovoltaika`|Pare Fwtovoltaika|`λίστα FwtovoltaikoApantisi`|
|GET|`/api/v1/energeia/syssoreftes`|Pare Syssoreftes|`λίστα SyssoreftisApantisi`|
|POST|`/api/v1/energeia/periorismos-fortiwn/proepiskopisi`|Proepiskopisi Periorismou Fortiwn|`ProepiskopisiPeriorismouApantisi`|
|POST|`/api/v1/energeia/periorismos-fortiwn/entoles`|Ektelesi Periorismou Fortiwn|`PeriorismosApantisi`|
|GET|`/api/v1/nero/istoriko`|Χρονοσειρά στάθμης, ανακύκλωσης και διαρροών|`λίστα IstorikoPorwnApantisi`|
|GET|`/api/v1/energeia/istoriko`|Χρονοσειρά ισχύος, αποθήκευσης και υδατικών ισοζυγίων|`λίστα IstorikoPorwnApantisi`|
|GET|`/api/v1/kindynoi`|Μετρήσεις και προβλέψεις εξωτερικών κινδύνων|`λίστα KindynosApantisi`|
|GET|`/api/v1/oximata`|Τηλεμετρία οχημάτων, επικοινωνία και πλήρωμα|`λίστα TilemetriaOximatos`|
|GET|`/api/v1/oximata/{id_oximatos}/apostoles`|Κατάσταση οχήματος και αποθηκευμένες διαδρομές|`KatastasiOximatos`|
|POST|`/api/v1/oximata/{id_oximatos}/apostoles`|Επιβεβαίωση προεπισκόπησης σχεδίου αποστολής|`ApantisiEntolisOximatos`|
|POST|`/api/v1/oximata/{id_oximatos}/apostoles/proepiskopisi`|Προεπισκόπηση πλήρους ενεργειακού κόστους αποστολής|`ProepiskopisiSxediou`|
|POST|`/api/v1/oximata/{id_oximatos}/anaklisi/proepiskopisi`|Ενέργεια, διαδρομή και επικοινωνία επιστροφής|`ProepiskopisiAnaklisis`|
|POST|`/api/v1/oximata/{id_oximatos}/anaklisi/entoles`|Επιβεβαίωση ανάκλησης με ορατή κατάσταση παραλαβής|`ApantisiEntolisOximatos`|
|POST|`/api/v1/oximata/{id_oximatos}/asfalis-stasi/proepiskopisi`|Συνέπειες ακινητοποίησης πριν από επιβεβαίωση|`ProepiskopisiStasis`|
|POST|`/api/v1/oximata/{id_oximatos}/asfalis-stasi/entoles`|Ασφαλής στάση μετά από επιβεβαιωμένη παραλαβή|`ApantisiEntolisOximatos`|
|POST|`/api/v1/oximata/{id_oximatos}/apostoles/{id_apostolis}/anavoli`|Αναβολή αποστολής πριν από την αναχώρηση|`ApantisiAnavolis`|
|GET|`/api/v1/synagermoi`|Λίστα συναγερμών με διαχωρισμό σοβαρότητας και κατάστασης (SHARED-02)|`λίστα SynagermosApantisi`|
|POST|`/api/v1/synagermoi/{id_synagermou}/anagnwrisi`|Αναγνώριση γνώσης συναγερμού (ΟΧΙ επίλυση - SHARED-02)|`AnagnwrisiSynagermouApantisi`|
|POST|`/api/v1/synagermoi/{id_synagermou}/epilysi`|Οριστική επίλυση συναγερμού με επαλήθευση (SHARED-08)|`EpilysiSynagermouApantisi`|
|GET|`/api/v1/senaria/kataigida-skonis`|Κατάσταση του fixture καταιγίδας σκόνης (STORM-01)|`KatastasiKataigidasApantisi`|
|POST|`/api/v1/senaria/kataigida-skonis/proepiskopisi`|Προεπισκόπηση επιλογών καταιγίδας με υπολογισμούς Golden Fixture (§6, STORM-05)|`ProepiskopisiSenariouApantisi`|
|POST|`/api/v1/senaria/kataigida-skonis/energopoiisi`|Ενεργοποίηση συνθηκών καταιγίδας σκόνης (STORM-02)|`EnergopoiisiSenariouApantisi`|
|POST|`/api/v1/senaria/{id_senariou}/apofaseis/proepiskopisi`|Συγκρίσεις αποφάσεων σεναρίου (STORM-05)|`ProepiskopisiSenariouApantisi`|
|POST|`/api/v1/senaria/{id_senariou}/apofaseis`|Υποβολή και έγκριση απόφασης συντονιστή για καταιγίδα (STORM-06, STORM-08)|`ApofasiApantisi`|
|GET|`/api/v1/senaria/{id_senariou}/xronologio`|Χρονολόγιο και ιστορικό αποφάσεων σεναρίου (STORM-08)|`λίστα IstorikoApofasisApantisi`|
|POST|`/api/v1/prosomoiwsi/vima`|Προώθηση προσομοιωμένου ρολογιού (Dev/Test only - CORE-13)|`VimaApantisi`|
|POST|`/api/v1/prosomoiwsi/epanafora`|Επαναφορά προσομοίωσης στα αρχικά δεδομένα (Dev/Test only)|`EpanaforaApantisi`|
|POST|`/api/v1/senaria/prokathorismena/{kodikos}/energopoiisi`|Εκπαιδευτική αστοχία ή αποκατάσταση|`EnergopoiisiSenariouApantisi`|
|GET|`/api/v1/senaria/prokathorismena`|Διαθέσιμα εκπαιδευτικά σενάρια|`λίστα string`|
|GET|`/api/v1/istoriko-elegxou`|Ανάκτηση αμετάβλητου ιστορικού ελέγχου (Audit Trail)|`λίστα IstorikoApantisi`|

Σύνολο:70 λειτουργίες HTTP. Τα σφάλματα400/401/403/404/409/422/500/503 χρησιμοποιούν `ApantisiSfalmatosSxhma`. Η ύπαρξη μοντέλου σφάλματος δεν σημαίνει ότι κάθε endpoint προκαλεί όλους τους κωδικούς.

Η εντολή εξαγωγής είναι `uv run --frozen python -m scripts.eksagogi_symvolaiou`. Η δοκιμή συμβολαίων απαιτεί ρητό σχήμα επιτυχίας για κάθε λειτουργία. Τα ελεύθερα,ετερογενή ιστορικά στιγμιότυπα δηλώνονται ως JSON τιμές μέσα σε συγκεκριμένα πεδία· ο εξωτερικός φάκελος της απόκρισης είναι τυποποιημένος.
