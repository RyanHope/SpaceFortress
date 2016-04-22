;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Helper functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defmacro defp (&rest body)
  `(p-fct ',body))

(defun run-until-break (&key (real-time t))
  (run-until-condition (lambda () nil) :real-time real-time))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Model initialization
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(clear-all)

(define-model spacefortress)

(jni-register-event-hook :break (lambda () (schedule-break-after-all)))

(sgp :jni-hostname "127.0.0.1"
     :jni-port 5555
     :jni-sync t
     :jni-remote-config (:obj ("General" . (:obj ("sound" . (:obj ("value" . :F)))
                                                 ("games_per_session" . (:obj ("value" . 0)))
                                                 ("game_time" . (:obj ("value" . 0)))))
                              ("Missile" . (:obj ("missile_max" . (:obj ("value" . 0)))))
                              ("Mine" . (:obj ("mine_exists" . (:obj ("value" . :F))))))
     )

(sgp :needs-mouse nil
     :v t
     :esc t
     :randomize-time nil
     :dual-execution-stages t
     :epl t
     :er t
     :ul t
     :ppm 1
     :alpha .8
     :egs .5
     ;  :lf .5
     ;  :bll .5
     ;  :mp 18
     ;  :rt -3
     ;  :ans .25
     )

(dolist (c '(study-mines avoid-shell avoid-border avoid-fortress shoot fly))
  (define-chunks-fct (list (list c))))

(defmethod home-hands ((mtr-mod motor-module))
  (setf (loc (left-hand mtr-mod)) #(3 4))
  (setf (fingers (left-hand mtr-mod))
    (list (list 'index #(0 0)) ;; d
          (list 'middle #(-1 -1)) ;; w
          (list 'ring #(-2 0)) ;; a
          (list 'pinkie #(-3 1)) ;; shift
          (list 'thumb #(1 2)))) ;; space
    (setf (loc (right-hand mtr-mod)) #(7 4))
    (setf (fingers (right-hand mtr-mod))
      (list (list 'index #(0 0)) ;; j
            (list 'middle #(1 0)) ;; k
            (list 'ring #(2 0)) ;; l
            (list 'pinkie #(5 0)) ;; enter
            (list 'thumb #(-1 2))))) ;; space

(home-hands (get-module :motor))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Productions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; Init
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **init-goal**
  ?goal> buffer empty state free
  ==>
  +goal> setting-fortress-exists :f setting-mine-exists :f setting-bonus-exists :f
  )

;;; Retrievals
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **retrieve-fortress-exists**
  =goal> setting-fortress-exists :f
  ?retrieval> state free
  ==>
  +retrieval> setting-fortress-exists t
  )

(defp **retrieve-mine-exists**
  =goal> setting-mine-exists :f
  ?retrieval> state free
  ==>
  +retrieval> setting-mine-exists t
  )

(defp **retrieve-bonus-exists**
  =goal> setting-bonus-exists :f
  ?retrieval> state free
  ==>
  +retrieval> setting-bonus-exists t
  )

;;; Retrievals storage
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **store-fortress-exists**
  =goal> setting-fortress-exists :f
  =retrieval> setting-fortress-exists t
  ==>
  *goal> setting-fortress-exists t
  )

(defp **store-mine-exists**
  =goal> setting-mine-exists :f
  =retrieval> setting-mine-exists t
  ==>
  *goal> setting-mine-exists t
  )

(defp **store-bonus-exists**
  =goal> setting-bonus-exists :f
  =retrieval> setting-bonus-exists t
  ==>
  *goal> setting-bonus-exists t
  )

;;; Move eyes
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **move-eyes-to-ship**
  ?visual-location> state free
  ?visual> state free
  ==>
  +visual-location> kind ship
  )

(defp **move-eyes-to-fortress**
  ?visual-location> state free
  ?visual> state free
  ==>
  +visual-location> kind fortress
  )

;;; Attend objects
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **attend-ship**
  =visual-location> kind ship
  ?visual-location> state free
  ?visual> state free
  ==>
  +visual> isa move-attention screen-pos =visual-location
  )

(defp **attend-fortress**
  =visual-location> kind fortress
  ?visual-location> state free
  ?visual> state free
  ==>
  +visual> isa move-attention screen-pos =visual-location
  )

;;; Imagine Visual Objects
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **imagine-object**
  =visual>
  ?imaginal> state free
  ==>
  +imaginal> =visual
  )

;;; Manual Actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **punch-thrust-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  ?manual> processor free
  ?manual-left> middle free middle up
  ==>
  +manual> isa delayed-punch hand left finger middle
  )

(defp **punch-left-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  ?manual> processor free
  ?manual-left> ring free ring up
  ==>
  +manual> isa delayed-punch hand left finger ring
  )

(defp **punch-right-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  ?manual> processor free
  ?manual-left> index free index up
  ==>
  +manual> isa delayed-punch hand left finger index
  )

(defp **punch-shoot-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  ?manual> processor free
  ?manual-left> thumb free thumb up
  ==>
  +manual> isa delayed-punch hand left finger thumb
  )

(defp **punch-iff-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  =goal> setting-mine-exists t
  ?manual> processor free
  ?manual-right> index free index up
  ==>
  +manual> isa delayed-punch hand right finger index
  )

(defp **punch-shots-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  =goal> setting-bonus-exists t
  ?manual> processor free
  ?manual-right> middle free middle up
  ==>
  +manual> isa delayed-punch hand right finger middle
  )

(defp **punch-pnts-key**
  =imaginal> kind =kind screen-x =screen-x screen-y =screen-y orientation =orientation velocity =velocity
  =goal> setting-bonus-exists t
  ?manual> processor free
  ?manual-right> ring free ring up
  ==>
  +manual> isa delayed-punch hand right finger ring
  )
