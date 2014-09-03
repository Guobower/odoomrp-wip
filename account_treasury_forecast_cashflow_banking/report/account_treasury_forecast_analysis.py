# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, tools


class ReportAccountTreasuryForecastAnalysis(models.Model):
    _inherit = "report.account.treasury.forecast.analysis"

    def init(self, cr):
        tools.drop_view_if_exists(cr,
                                  'report_account_treasury_forecast_analysis')
        cr.execute("""
            create or replace view report_account_treasury_forecast_analysis
                as (
                select
                    treasury_id,
                    CASE WHEN tfl.line_type='receivable' THEN amount
                    ELSE -amount
                    END as amount,
                    payment_mode_id,
                    'out' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_line tfl on tf.id =
                        tfl.treasury_id
                union
                select
                    treasury_id,
                    amount as amount,
                    payment_mode_id,
                    flow_type as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_cashflow tcf on tf.id =
                        tcf.treasury_id
                union
                select
                    treasury_id,
                    -tfii.total_amount as amount,
                    tfii.payment_mode_id,
                    'out' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_in_invoice_rel tfiir on tf.id =
                        tfiir.treasury_id inner join
                    account_treasury_forecast_invoice tfii on tfii.id =
                        tfiir.in_invoice_id
                union
                select
                    treasury_id,
                    tfio.total_amount as amount,
                    tfio.payment_mode_id,
                    'in' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_out_invoice_rel tfior on tf.id =
                        tfior.treasury_id inner join
                    account_treasury_forecast_invoice tfio on tfio.id =
                        tfior.out_invoice_id
            )""")
