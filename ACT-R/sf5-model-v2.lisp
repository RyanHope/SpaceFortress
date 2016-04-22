;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Helper functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun run-until-break (&key (real-time t))
  (run-until-condition (lambda () nil) :real-time real-time))

(defun degrees (x) (* x (/ 180 pi)))

(defun to-target-orientation(selfx selfy targx targy)
  (round (mod (- (degrees (atan (- targx selfx) (- selfy targy))) 90) 360)))

(defun point-on-line (px py x1 y1 x2 y2)
  (= (- py y1) (* (/ (- y2 y1) (- x2 x1)) (- px x1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Model initialization
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(clear-all)

(define-model spacefortress)

(jni-register-event-hook :break (lambda () (schedule-break-after-all)))

(sgp :jni-hostname "127.0.0.1"
     :jni-port 5555
     :jni-sync t
     :jni-remote-config (:obj ("Mine" . (:obj ("mine_exists" . (:obj ("value" . :F)))))))

(sgp :needs-mouse nil
     :v t
     :esc t
     :er t
     :ul t
     :ppm 1
     :mas 1
     :mp 1
     :randomize-time nil
     :dual-execution-stages t
     )

;;; Goals
;(chunk-type study-mine-letters state)
;(chunk-type monitor)
;(chunk-type shoot-fortress subgoal)
;(chunk-type shoot-mine subgoal)
;(chunk-type avoid-shells subgoal)
;(chunk-type avoid-fortress subgoal)
;(chunk-type avoid-warping subgoal)
;(chunk-type avoid-mine subgoal)

;;; New chunk types
; (chunk-type settings mines)
; (chunk-type game)
; (chunk-type (token-location (:include visual-location)) orientation velocity)
; (chunk-type (token-object (:include visual-object)) orientation velocity)
; (chunk-type (ship (:include token-object)))
; (chunk-type (fortress (:include token-object)))
; (chunk-type (mine (:include token-object)))
; (chunk-type (shell (:include token-object)))
; (chunk-type (missile (:include token-object)))
; (chunk-type (rect-location (:include visual-location)) top bottom left right)
; (chunk-type (rect-object (:include visual-object)) top bottom left right)
; (chunk-type (world-border (:include rect-object)))
; (chunk-type mine-letters (letter1 t) (letter2 t) (letter3 t))

(dolist (c '(study-mines avoid-shell avoid-border avoid-fortress shoot fly))
  (define-chunks-fct (list (list c))))

;(set-hand-location left 3 4)
;(move-a-finger (get-module :motor) 'left 'middle 1 -1.57)
;(set-hand-location right 12 4)

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

(defp **start**
  ?goal> buffer empty
  ?retrieval> state free
  ==>
  +goal> game-settings t game-number t game-state t
  +retrieval> has-mines
  )

(defp **prep-new-game**
  =goal> game-settings t game-number t game-state t
  =retrieval> isa settings
  ==>
  *goal> settings =retrieval
  )

(defp **get-game-number**
  =goal> - settings t number t state t
  ?visual-location> state free buffer empty
  ==>
  +visual-location> kind text color "yellow"
  )

(defp **attend-game-number**
  =goal> - settings t number t state t
  =visual-location> kind text color "yellow"
  ?visual> state free buffer empty
  ==>
  +visual> isa move-attention screen-pos =visual-location
  )

(defp **store-game-number**
  =goal> - settings t number t state t
  =visual> kind text color "yellow" number =number
  ==>
  *goal> number =number
  )

(defp **ready-to-study-mines**
  =goal> - settings t - number t state t
  ?manual> processor free
  ?manual-right> pinkie free pinkie up
  ==>
  +manual> isa delayed-punch hand right finger pinkie
  *goal> state study-mines
  +imaginal> isa mine-letters
  )

(defp **get-mine-letter-unstuffed**
  =goal> state study-mines
  ?visual-location> state free buffer empty
  ?manual> state free
  ?visual> state free buffer empty
  ?imaginal> - buffer empty state free
  =imaginal> letter1 =letter1 letter2 =letter2 letter3 =letter3
  ==>
  =imaginal>
  +visual-location> kind text color "white" - value =letter1 - value =letter2 - value =letter3
  )

(defp **get-mine-letter-stuffed**
  =goal> state study-mines
  =visual-location> color "yellow"
  ?manual> state free
  ?visual> state free
  ?imaginal> - buffer empty state free
  =imaginal> letter1 =letter1 letter2 =letter2 letter3 =letter3
  ==>
  =imaginal>
  +visual-location> kind text color "white" - value =letter1 - value =letter2 - value =letter3
  )

(defp **attend-letter**
  =goal> state study-mines
  =imaginal> letter1 =letter1 letter2 =letter2 letter3 =letter3
  =visual-location> kind text color "white" - value =letter1 - value =letter2 - value =letter3
  ?visual> state free
  ?imaginal> - buffer empty
  ==>
  =imaginal>
  +visual> isa move-attention screen-pos =visual-location
  =visual-location>
  )

(defp **store-letter-1**
  =goal> state study-mines
  =visual> kind text color "white" value =letter
  =imaginal> letter1 t - letter2 =letter - letter3 =letter
  ?imaginal> - buffer empty state free
  ==>
  *imaginal> letter1 =letter
  -visual-location>
  )

(defp **store-letter-2**
  =goal> state study-mines
  =visual> kind text color "white" value =letter
  =imaginal> - letter1 =letter letter2 t - letter3 =letter
  ?imaginal> - buffer empty state free
  ==>
  *imaginal> letter2 =letter
  -visual-location>
  )

(defp **store-letter-3**
  =goal> state study-mines
  =visual> kind text color "white" value =letter
  =imaginal> - letter1 =letter - letter2 =letter letter3 t
  ?imaginal> - buffer empty state free
  ==>
  *imaginal> letter3 =letter
  -visual-location>
  )

(defp **done-studying-letters**
  =goal> state study-mines
  =imaginal> - letter1 t - letter2 t - letter3 t
  ?manual> processor free
  ?manual-right> pinkie free pinkie up
  ==>
  +manual> isa delayed-punch hand right finger pinkie
  +goal> state fly
  )

(defp **thrust**
  =goal> state fly
  ?manual> processor free
  ?manual-left> pinkie free middle up
  ==>
  +manual> isa delayed-punch hand left finger middle
  )


(defp **left**
  =goal> state fly
  ?manual> processor free
  ?manual-left> pinkie free ring up
  ==>
  +manual> isa delayed-punch hand left finger ring
  )


(defp **right**
  =goal> state fly
  ?manual> processor free
  ?manual-left> pinkie free index up
  ==>
  +manual> isa delayed-punch hand left finger index
  )
