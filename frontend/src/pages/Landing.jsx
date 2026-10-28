import { t } from '../i18n/index.js'
import { Link } from 'react-router-dom'
import { Icon, Logo, PublicHeader } from '../components/ui.jsx'

function ParcelDrawing() {
  return (
    <svg
      className="parcel-drawing"
      viewBox="0 0 560 470"
      fill="none"
      role="img"
      aria-label={t("original_illustration_of_a_box_with_its_own")}
    >
      <defs>
        <pattern id="guides" width="36" height="36" patternUnits="userSpaceOnUse">
          <path d="M36 0H0V36" stroke="#41574d" strokeWidth=".5" />
        </pattern>
      </defs>
      <rect width="560" height="470" fill="url(#guides)" />
      <path d="M60 395H500M90 55V430" stroke="#81978b" strokeDasharray="3 6" />
      <path
        d="m135 158 176-85 149 92-172 89-153-96Z"
        fill="#dce4d2"
        stroke="#101F20"
        strokeWidth="2"
      />
      <path d="M135 158v176l153 96V254l-153-96Z" fill="#aabe9d" stroke="#101F20" strokeWidth="2" />
      <path d="M288 254v176l172-92V165l-172 89Z" fill="#c5f278" stroke="#101F20" strokeWidth="2" />
      <path d="m210 122 151 96v84l31-17v-82l-151-97-31 16Z" fill="#203934" />
      <path d="m318 285 109-58v76l-109 58v-76Z" fill="#F4F6F2" stroke="#101F20" strokeWidth="1.5" />
      <path d="m332 285 81-43M332 300l49-26M332 319l81-43" stroke="#101F20" strokeWidth="3" />
      <path d="M43 86V61h25M500 383v26h-26" stroke="#C5F278" strokeWidth="3" />
      <text x="42" y="39" fill="#C5F278" fontSize="12" fontFamily="monospace" letterSpacing="2">{t("identification_system")}</text>
      <text x="42" y="452" fill="#dce4d2" fontSize="12" fontFamily="monospace">{t("cj_own_identity_independent_qr")}</text>
    </svg>
  )
}

export default function Landing() {
  return (
    <div className="landing">
      <a className="skip-link" href="#contenido">{t("skip_to_content")}</a>
      <PublicHeader />
      <main id="contenido" tabIndex="-1">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">
              <span className="status-dot" />{' '}{t("logistics_with_a_clear_identity")}</p>
            <h1>{t("every_box")}<br />{t("in_its_place")}<br />
              <em>{t("under_control")}</em>
            </h1>
            <p className="hero-description">{t("stop_searching_through_scattered_data_identify_organize_and")}</p>
            <div className="hero-actions">
              <Link className="button button-dark" to="/registro">{t("get_started_with_logistech")}{' '}<Icon name="arrow" />
              </Link>
              <Link className="text-link" to="/login">{t("i_already_have_an_account")}{' '}<span aria-hidden="true">↗</span>
              </Link>
            </div>
            <p className="hero-note">{t("role_based_access_company_scoped_data_alternative_identification")}</p>
          </div>
          <div className="hero-visual">
            <div className="visual-label">
              <span>{t("logistech_operations")}</span>
              <span>WEB 2.0</span>
            </div>
            <ParcelDrawing />
            <div className="visual-footer">
              <span className="status-dot" />
              <span>{t("control_starts_with_knowing_what_you_have")}</span>
            </div>
          </div>
        </section>
        <section className="product-band" id="producto">
          <p className="eyebrow">{t("less_friction_more_clarity")}</p>
          <h2>{t("one_control_sheet")}<br />{t("all_the_context_you_need")}</h2>
          <p>{t("clear_categories_identifiable_boxes_and_access_for_authorized")}</p>
        </section>
        <section className="process" aria-label={t("available_process")}>
          <div className="section-heading">
            <p className="eyebrow">{t("from_registration_to_lookup")}</p>
            <h2>{t("order_at_every_step")}</h2>
          </div>
          <div className="process-grid">
            {[
              [
                '01',
                t("classify_with_care"),
                t("organize_categories_and_identify_fragile_and_perishable_goods"),
              ],
              [
                '02',
                t("give_it_an_identity"),
                t("register_each_box_with_its_own_internal_identifier"),
              ],
              [
                '03',
                t("find_the_context"),
                t("search_filter_and_view_product_quantity_branch_priority"),
              ],
            ].map(([n, title, copy]) => (
              <article key={n}>
                <span className="step-number">{n}</span>
                <h3>{title}</h3>
                <p>{copy}</p>
                <Icon name="arrow" />
              </article>
            ))}
          </div>
        </section>
        <section className="capabilities">
          <div>
            <p className="eyebrow">{t("what_you_can_do_today")}</p>
            <h2>{t("practical_tools")}<br />{t("clear_permissions")}</h2>
            <p>{t("operators_work_with_their_boxes_administrators_organize_their")}</p>
            <Link className="text-link" to="/login">{t("enter_the_workspace")}{' '}<Icon name="arrow" />
            </Link>
          </div>
          <ul>
            {[
              t("secure_registration_and_sign_in"),
              t("categories_with_fragile_and_perishable_conditions"),
              t("boxes_with_manual_search_and_their_own_identifiers"),
              t("actions_based_on_role_and_status"),
            ].map((text) => (
              <li key={text}>
                <Icon name="check" />
                {text}
              </li>
            ))}
          </ul>
        </section>
        <section className="future-note">
          <span className="badge">{t("on_the_roadmap")}</span>
          <p>{t("camera_and_qr_scanning_advanced_receptions_history_and")}</p>
        </section>
        <section className="closing-cta">
          <div>
            <p className="eyebrow">{t("the_next_step_is_simple")}</p>
            <h2>{t("start_putting")}<br />{t("things_in_order")}</h2>
          </div>
          <Link className="button button-primary" to="/registro">{t("create_my_account")}{' '}<Icon name="arrow" />
          </Link>
        </section>
      </main>
      <footer className="public-footer">
        <Logo compact />
        <p>{t("academic_project_tecsup")}<br />
          <span>{t("cloud_solutions_development")}</span>
        </p>
        <Link to="/estado">{t("service_status")}{' '}<Icon name="arrow" />
        </Link>
      </footer>
    </div>
  )
}
